"""REB remote MCP transport + OAuth 2.1 PKCE + isolated tenant workspaces.

Production deployment REQUIRES a trusted HTTPS reverse proxy. No remote public
operations are enabled by default. No dependency on a hosted auth provider.
The local owner must create accounts with `reb-remote user-add USERNAME`.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs

from .errors import REBError
from .storage import Store
from .mcp_stdio import dispatch, TOOLS

MAX_BODY = 1024 * 1024
USER_RE = re.compile(r'^[a-zA-Z0-9_-]{3,64}$')

def _hash(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()

def make_password(password: str) -> str:
    if len(password) < 12:
        raise REBError('Password must have at least 12 characters')
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310000)
    return f'pbkdf2_sha256$310000${salt.hex()}${digest.hex()}'

def verify_password(password: str, stored: str) -> bool:
    try:
        algo, n, salt, digest = stored.split('$')
        if algo != 'pbkdf2_sha256' or int(n) < 100000 or int(n) > 1000000:
            return False
        return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),int(n)),bytes.fromhex(digest))
    except (ValueError, TypeError):
        return False

def _secure_redirect(uri: str) -> bool:
    try:
        u = urlparse(uri)
        return not u.fragment and not u.username and not u.password and bool(u.hostname) and (
            (u.scheme == 'https' and bool(u.netloc)) or
            (u.scheme == 'http' and u.hostname in ('localhost','127.0.0.1','[::1]','::1')))
    except ValueError:
        return False

class Accounts:
    def __init__(self, directory: str | Path):
        self.root = Path(directory).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / 'remote-identity.sqlite3'
        self.lock = threading.RLock()
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS clients(id TEXT PRIMARY KEY, name TEXT NOT NULL, redirects TEXT NOT NULL, created_at INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS codes(code_hash TEXT PRIMARY KEY, username TEXT NOT NULL, client_id TEXT NOT NULL, redirect_uri TEXT NOT NULL, challenge TEXT NOT NULL, scope TEXT NOT NULL, expiry INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS tokens(token_hash TEXT PRIMARY KEY, username TEXT NOT NULL, client_id TEXT NOT NULL, kind TEXT NOT NULL, expiry INTEGER NOT NULL);
            ''')

    def connect(self):
        db = sqlite3.connect(self.path,timeout=15)
        db.row_factory = sqlite3.Row
        return db

    def add_user(self, username, password):
        if not USER_RE.fullmatch(username):
            raise REBError('Username must be 3-64 letters, numbers, _ or -')
        hashed = make_password(password)
        with self.lock, self.connect() as db:
            db.execute('INSERT INTO users VALUES (?,?)', (username,hashed))
        return username

    def authenticate(self, username, password):
        with self.connect() as db:
            row = db.execute('SELECT password_hash FROM users WHERE username=?',(username,)).fetchone()
        # Same cost even if account missing; do not reveal user enumeration.
        dummy = 'pbkdf2_sha256$310000$'+ ('00'*16) +'$'+('00'*32)
        return verify_password(password, row['password_hash'] if row else dummy) and row is not None

    def register_client(self, name, redirects):
        if not isinstance(redirects,list) or not (1 <= len(redirects) <= 8) or any(not isinstance(u,str) or not _secure_redirect(u) for u in redirects):
            raise REBError('redirect_uris must be explicit HTTPS or localhost URLs')
        cid = secrets.token_urlsafe(24)
        with self.lock,self.connect() as db:
            db.execute('INSERT INTO clients VALUES(?,?,?,?)',(cid,str(name)[:150],json.dumps(redirects),int(time.time())))
        return cid

    def client_valid(self, cid, uri):
        with self.connect() as db:
            row=db.execute('SELECT redirects FROM clients WHERE id=?',(cid,)).fetchone()
        return bool(row and uri in json.loads(row['redirects']))

    def authorize(self, username, cid, uri, challenge, scope):
        if not self.client_valid(cid,uri) or not re.fullmatch(r'[A-Za-z0-9_-]{43,128}',challenge):
            raise REBError('Invalid OAuth authorization request')
        code=secrets.token_urlsafe(32)
        with self.lock,self.connect() as db:
            db.execute('INSERT INTO codes VALUES(?,?,?,?,?,?,?)',(_hash(code),username,cid,uri,challenge,scope,int(time.time())+120))
        return code

    def _tokens(self, username, cid):
        access=secrets.token_urlsafe(32); refresh=secrets.token_urlsafe(32); now=int(time.time())
        with self.connect() as db:
            db.executemany('INSERT INTO tokens VALUES (?,?,?,?,?)', [(_hash(access),username,cid,'access',now+3600),(_hash(refresh),username,cid,'refresh',now+2592000)])
        return {'access_token':access,'token_type':'Bearer','expires_in':3600,'refresh_token':refresh,'scope':'reb:projects'}

    def exchange_code(self, code, client_id, redirect_uri, verifier):
        if not isinstance(verifier,str) or not re.fullmatch(r'[A-Za-z0-9._~-]{43,128}',verifier):
            raise REBError('Invalid code_verifier')
        derived = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode('ascii')).digest()).rstrip(b'=').decode()
        with self.lock,self.connect() as db:
            row=db.execute('SELECT * FROM codes WHERE code_hash=?',(_hash(code),)).fetchone()
            if not row or row['expiry']<time.time() or row['client_id']!=client_id or row['redirect_uri']!=redirect_uri or not hmac.compare_digest(derived,row['challenge']):
                raise REBError('Invalid or expired authorization code')
            db.execute('DELETE FROM codes WHERE code_hash=?',(_hash(code),))
            username = row['username']
        return self._tokens(username,client_id)

    def refresh(self, token, cid):
        with self.lock,self.connect() as db:
            row=db.execute('SELECT * FROM tokens WHERE token_hash=?',(_hash(token),)).fetchone()
            if not row or row['kind']!='refresh' or row['client_id']!=cid or row['expiry']<time.time():
                raise REBError('Invalid refresh token')
            db.execute('DELETE FROM tokens WHERE token_hash=?',(_hash(token),))
            username = row['username']
        return self._tokens(username,cid)

    def revoke(self, token, cid):
        if not isinstance(token,str) or not 1 <= len(token) <= 256: return
        with self.lock,self.connect() as db:
            db.execute('DELETE FROM tokens WHERE token_hash=? AND client_id=?',(_hash(token),cid))

    def owner(self, token):
        if not token or len(token)>256: return None
        with self.connect() as db:
            row=db.execute('SELECT username FROM tokens WHERE token_hash=? AND kind=? AND expiry>=?',(_hash(token),'access',int(time.time()))).fetchone()
        return row['username'] if row else None

    def workspace(self, username):
        if not USER_RE.fullmatch(username):
            raise REBError('Invalid workspace identity')
        # Use a stable digest, not user-controlled directory paths.
        return self.root / 'tenants' / (hashlib.sha256(username.encode()).hexdigest() + '.sqlite3')


def handler_factory(accounts: Accounts, issuer: str, allow_external=False):
    issuer=issuer.rstrip('/')
    if not (issuer.startswith('https://') or issuer.startswith('http://127.0.0.1:') or issuer.startswith('http://localhost:')):
        raise REBError('REB_PUBLIC_URL must use HTTPS or localhost for development')

    failures = {}
    failures_lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        server_version='REB-Remote/0.3'
        def log_message(self, format, *args):
            # No URLs, query params, credentials or business payloads in logs.
            pass
        def send(self, status, body, content_type='application/json', headers=None):
            content = json.dumps(body,ensure_ascii=False).encode('utf-8') if content_type=='application/json' else body.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type',content_type+'; charset=utf-8')
            self.send_header('Content-Length',str(len(content)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
            if issuer.startswith('https://'): self.send_header('Strict-Transport-Security','max-age=31536000')
            for k,v in (headers or {}).items():self.send_header(k,v)
            self.end_headers(); self.wfile.write(content)
        def read_body(self):
            try: n=int(self.headers.get('Content-Length','0'))
            except ValueError: raise REBError('Invalid content length')
            if n<=0 or n>MAX_BODY: raise REBError('Invalid body size')
            return self.rfile.read(n)
        def form(self):
            ct=self.headers.get('Content-Type','')
            raw=self.read_body()
            if 'application/json' in ct:
                value=json.loads(raw)
                if not isinstance(value,dict): raise REBError('JSON object required')
                return value
            if 'application/x-www-form-urlencoded' in ct:
                return {k:v[0] for k,v in parse_qs(raw.decode('utf-8'),keep_blank_values=True).items()}
            raise REBError('Unsupported Content-Type')
        def forbidden(self):
            return self.send(401,{'error':'invalid_token'},headers={'WWW-Authenticate':f'Bearer resource_metadata="{issuer}/.well-known/oauth-protected-resource"'})
        def authorize_params(self, d):
            cid=d.get('client_id',''); uri=d.get('redirect_uri',''); challenge=d.get('code_challenge','')
            if d.get('response_type')!='code' or d.get('code_challenge_method')!='S256' or not accounts.client_valid(cid,uri) or not re.fullmatch(r'[A-Za-z0-9_-]{43,128}',challenge):
                raise REBError('Unsupported OAuth authorization request')
            return cid,uri,challenge
        def do_GET(self):
            p=urlparse(self.path); q={k:v[0] for k,v in parse_qs(p.query).items()}
            if p.path=='/healthz':return self.send(200,{'status':'ok'})
            if p.path=='/.well-known/oauth-protected-resource':
                return self.send(200,{'resource':issuer+'/mcp','authorization_servers':[issuer], 'bearer_methods_supported':['header']})
            if p.path in ('/.well-known/oauth-authorization-server','/.well-known/openid-configuration'):
                return self.send(200,{'issuer':issuer,'authorization_endpoint':issuer+'/oauth/authorize','token_endpoint':issuer+'/oauth/token','registration_endpoint':issuer+'/oauth/register','revocation_endpoint':issuer+'/oauth/revoke',
                                      'response_types_supported':['code'],'grant_types_supported':['authorization_code','refresh_token'], 'token_endpoint_auth_methods_supported':['none'],'code_challenge_methods_supported':['S256'],'scopes_supported':['reb:projects']})
            if p.path=='/oauth/authorize':
                try:self.authorize_params(q)
                except REBError:return self.send(400,{'error':'invalid_request'})
                # Escaping all request-provided text prevents reflected XSS.
                fields=''.join(f'<input type="hidden" name="{html.escape(k,quote=True)}" value="{html.escape(str(q.get(k,"")),quote=True)}">' for k in ('client_id','redirect_uri','response_type','code_challenge','code_challenge_method','state','scope'))
                page='<html><head><meta charset="utf-8"><title>REB login</title></head><body><h2>Authorize REB</h2><p>Enter account credentials to grant access to your own projects.</p><form method="POST" action="/oauth/authorize">'+fields+'<label>User <input name="username" required></label><label>Password <input type="password" name="password" required></label><button type="submit">Approve access</button></form></body></html>'
                return self.send(200,page,'text/html')
            if p.path=='/mcp':
                if not self.bearer(): return self.forbidden()
                return self.send(405,{'error':'MCP GET/SSE not supported; use POST'},headers={'Allow':'POST'})
            return self.send(404,{'error':'not_found'})
        def bearer(self):
            a=self.headers.get('Authorization','')
            return accounts.owner(a[7:]) if a.startswith('Bearer ') else None
        def do_POST(self):
            p=urlparse(self.path).path
            try:
                if p=='/oauth/register':
                    body=self.form(); redirect=body.get('redirect_uris',[])
                    cid=accounts.register_client(body.get('client_name','REB client'),redirect)
                    return self.send(201,{'client_id':cid,'client_name':str(body.get('client_name','REB client'))[:150],'redirect_uris':redirect,'token_endpoint_auth_method':'none','grant_types':['authorization_code','refresh_token'],'response_types':['code']})
                if p=='/oauth/authorize':
                    body=self.form(); cid,uri,challenge=self.authorize_params(body)
                    username=body.get('username',''); password=body.get('password','')
                    # Coarse abuse prevention; production deployments must add a durable edge rate limiter.
                    addr=self.client_address[0] + ':' + str(username)
                    now=time.monotonic()
                    with failures_lock:
                        recent=[v for v in failures.get(addr,[]) if now-v<60]
                        failures[addr]=recent
                        if len(recent)>=5:
                            return self.send(429,{'error':'too_many_attempts'},headers={'Retry-After':'60'})
                    if not accounts.authenticate(username,password):
                        with failures_lock: failures[addr].append(now)
                        return self.send(401,{'error':'access_denied'})
                    with failures_lock: failures.pop(addr,None)
                    code=accounts.authorize(username,cid,uri,challenge,body.get('scope','reb:projects'))
                    sep='&' if '?' in uri else '?'
                    dest=uri+sep+urlencode({'code':code,'state':body.get('state','')})
                    return self.send(302,'', 'text/plain', {'Location':dest})
                if p=='/oauth/token':
                    b=self.form(); kind=b.get('grant_type')
                    if kind=='authorization_code': data=accounts.exchange_code(b.get('code',''),b.get('client_id',''),b.get('redirect_uri',''),b.get('code_verifier',''))
                    elif kind=='refresh_token':data=accounts.refresh(b.get('refresh_token',''),b.get('client_id',''))
                    else:return self.send(400,{'error':'unsupported_grant_type'})
                    return self.send(200,data)
                if p=='/oauth/revoke':
                    b=self.form()
                    accounts.revoke(b.get('token',''),b.get('client_id',''))
                    return self.send(200,{})
                if p=='/mcp':
                    username=self.bearer()
                    if not username:return self.forbidden()
                    msg=self.form()
                    if 'jsonrpc' not in msg or msg['jsonrpc']!='2.0':return self.send(400,{'error':'invalid_jsonrpc'})
                    if msg.get('method')=='tools/call' and not allow_external and msg.get('params',{}).get('name') in ('reb_run_mission','reb_research_sources','reb_consult_specialist'):
                        return self.send(403,{'error':'external_services_disabled','detail':'Set REB_REMOTE_ALLOW_EXTERNAL=1 after reviewing operator consent and billing'})
                    with Store(accounts.workspace(username)) as store:
                        result=dispatch(msg,store)
                    if result is None:return self.send(202,'','text/plain')
                    return self.send(200,result)
                return self.send(404,{'error':'not_found'})
            except (REBError, ValueError, KeyError, json.JSONDecodeError) as ex:
                return self.send(400,{'error':'invalid_request','detail':str(ex)[:160]})
            except Exception:
                return self.send(500,{'error':'internal_error'})
    return Handler

def serve_remote(host='127.0.0.1',port=8787,root=None,public_url=None):
    root=root or os.getenv('REB_REMOTE_DATA',str(Path.home()/'.reb'/'remote'))
    public_url=public_url or os.getenv('REB_PUBLIC_URL',f'http://127.0.0.1:{port}')
    if host not in ('127.0.0.1','localhost','::1') and not public_url.startswith('https://'):
        raise REBError('Public bind requires HTTPS public URL with reverse proxy')
    accounts=Accounts(root)
    server=ThreadingHTTPServer((host,port),handler_factory(accounts,public_url,os.getenv('REB_REMOTE_ALLOW_EXTERNAL')=='1'))
    print('REB remote MCP listening on '+host+':'+str(port),flush=True)
    server.serve_forever()

def main(argv=None):
    import argparse,getpass
    ap=argparse.ArgumentParser(description='REB OAuth MCP server and user provisioning')
    s=ap.add_subparsers(dest='cmd',required=True)
    run=s.add_parser('serve');run.add_argument('--host',default=os.getenv('REB_HOST','127.0.0.1'));run.add_argument('--port',type=int,default=int(os.getenv('REB_PORT','8787')))
    add=s.add_parser('user-add');add.add_argument('username')
    a=ap.parse_args(argv)
    if a.cmd=='serve':serve_remote(a.host,a.port)
    elif a.cmd=='user-add':
        pw=getpass.getpass('REB password (12+ chars): ')
        Accounts(os.getenv('REB_REMOTE_DATA',str(Path.home()/'.reb'/'remote'))).add_user(a.username,pw)
        print('Account created:',a.username)

if __name__=='__main__':main()
