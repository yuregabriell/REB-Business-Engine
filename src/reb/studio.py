"""Local-only human interface for nontechnical founders.

No remote deployment or authentication; binds to 127.0.0.1 only.
"""
import json
import mimetypes
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from .storage import Store
from .engine import diagnose, recommend_experiment
from .finance import financial_scenario
from .errors import REBError
from .agents import AGENTS
from .knowledge import find_methods
from .blueprint import build_blueprint

ASSET_ROOT = Path(__file__).parent / "web"


def build_handler(db_path=None):
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        server_version = "REBStudio/0.1"

        def send(self, status: int, data: bytes, mime: str):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)

        def j(self, status, payload):
            self.send(status, json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8"), "application/json; charset=utf-8")

        def trusted_host(self):
            return self.headers.get('Host', '') in {
                f'127.0.0.1:{self.server.server_port}',
                f'localhost:{self.server.server_port}',
            }

        def do_GET(self):
            if not self.trusted_host(): return self.j(403, {'error':'Host not allowed'})
            parsed = urlparse(self.path)
            p = parsed.path
            qs = parse_qs(parsed.query)
            try:
                if p == '/api/session': return self.j(200, {'csrf':token})
                if p == '/api/methods': return self.j(200, find_methods(qs.get('q',[''])[0]))
                if p == '/api/agents': return self.j(200, [{'key':a.key,'name':a.title,'mission':a.mission} for a in AGENTS])
                if p.startswith('/api/'):
                    with Store(db_path) as s:
                        if p == '/api/projects': return self.j(200, s.list_projects())
                        if p == '/api/project': return self.j(200, s.export(qs.get('id',[''])[0]))
                        if p == '/api/blueprint': return self.j(200, build_blueprint(s, qs.get('id',[''])[0]))
                        if p == '/api/diagnose': return self.j(200, diagnose(s, qs.get('id',[''])[0]))
                    return self.j(404, {'error':'Not found'})
                asset = {'/':'index.html','/index.html':'index.html','/app.js':'app.js','/styles.css':'styles.css'}.get(p)
                if not asset: return self.j(404, {'error':'Not found'})
                data = (ASSET_ROOT / asset).read_bytes()
                return self.send(200, data, {'index.html':'text/html; charset=utf-8','app.js':'text/javascript; charset=utf-8','styles.css':'text/css; charset=utf-8'}[asset])
            except REBError as exc: return self.j(400, {'error':str(exc)})

        def do_POST(self):
            if not self.trusted_host(): return self.j(403, {'error':'Host not allowed'})
            origin = self.headers.get('Origin')
            expected = 'http://127.0.0.1:' + str(self.server.server_port)
            if origin and origin not in {expected, 'http://localhost:' + str(self.server.server_port)}:
                return self.j(403, {'error':'Origin not allowed'})
            if self.headers.get('X-REB-Token') != token:
                return self.j(403, {'error':'Invalid session token'})
            size = self.headers.get('Content-Length', '0')
            try: length = int(size)
            except ValueError: return self.j(400, {'error':'Invalid content length'})
            if length < 0 or length > 128_000: return self.j(413, {'error':'Payload too large'})
            try:
                data = json.loads(self.rfile.read(length))
                if not isinstance(data,dict): raise ValueError('Expected JSON object')
                with Store(db_path) as s:
                    if self.path == '/api/projects':
                        response=s.add_project(data['name'],data['idea'], data.get('market','Portugal'),data.get('stage','idea'),data.get('budget','0'), data.get('objective','Validar procura'))
                    elif self.path == '/api/evidence':
                        response=s.add_evidence(data['project_id'],data['claim'],data.get('url',''),data.get('status','unverified'))
                    elif self.path == '/api/experiments':
                        response=s.add_experiment(data['project_id'],data['hypothesis'],data['metric'],data['target'],data.get('cap','0'))
                    elif self.path == '/api/journal':
                        response=s.add_journal(data['project_id'],data['body'],data.get('kind','activity'),data.get('revenue','0'),data.get('cost','0'),int(data.get('customers',0)))
                    elif self.path == '/api/finance':
                        response=financial_scenario(data['price'],data['variable'],data['fixed'],int(data['units']),data.get('cash','0'),data.get('cac','0'))
                    else: return self.j(404, {'error':'Not found'})
                return self.j(201,response)
            except (KeyError,ValueError,TypeError,REBError) as exc: return self.j(400, {'error': str(exc)})

        def log_message(self, fmt, *args):
            # No sensitive project text in default stdout logs.
            pass
    return Handler


def serve(db_path=None, port: int=8765):
    if not 1024 <= port <= 65535: raise REBError('Porta deve estar entre 1024 e 65535.')
    server = ThreadingHTTPServer(('127.0.0.1',port),build_handler(db_path))
    print(f'REB Studio local: http://127.0.0.1:{server.server_port} (Ctrl+C para parar)')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
