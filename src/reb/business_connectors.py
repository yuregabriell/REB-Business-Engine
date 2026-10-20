"""Deliberately narrow read-only integrations; keep credentials out of project history.

Each integration requires explicit operator approval and a provider token. Third-party
results are unverified claims until sourced, reconciled and reviewed.
"""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .errors import REBError


def hubspot_read(kind: str, *, limit: int=20, approved: bool=False, opener=urlopen) -> dict:
    """Read a small sample of HubSpot contacts or deals, never writes or exports tokens."""
    if not approved:
        raise REBError('É necessária autorização explícita de leitura de CRM')
    if kind not in ('contacts','deals') or not isinstance(limit,int) or not 1 <= limit <= 100:
        raise REBError('Recurso ou limite inválido')
    token=os.environ.get('HUBSPOT_PRIVATE_APP_TOKEN','').strip()
    if not token:
        raise REBError('HUBSPOT_PRIVATE_APP_TOKEN não configurado')
    props={'contacts':'firstname,lastname,email','deals':'dealname,amount,dealstage'}[kind]
    url='https://api.hubapi.com/crm/v3/objects/'+kind+'?'+urlencode({'limit':limit,'properties':props})
    req=Request(url,headers={'Authorization':'Bearer '+token,'Accept':'application/json','User-Agent':'REB-business-engine/0.3'})
    try:
        with opener(req,timeout=15) as response:
            raw=response.read(500_001)
            if len(raw)>500_000:raise REBError('CRM response exceeds size limit')
    except (HTTPError,URLError,TimeoutError) as exc:
        raise REBError('Não foi possível ler o CRM autorizado') from exc
    try:
        data=json.loads(raw)
        if not isinstance(data.get('results'),list):raise ValueError('missing results')
        # Do not include emails or personally identifying information by default.
        items=[]
        for x in data['results'][:limit]:
            p=x.get('properties') or {}
            if kind=='contacts':
                items.append({'id':x.get('id'),'has_email':bool(p.get('email'))})
            else:
                items.append({'id':x.get('id'),'dealstage':p.get('dealstage'),'amount':p.get('amount')})
        return {'provider':'HubSpot','resource':kind,'count_returned':len(items),'records':items,'verified':False,'note':'Dados internos lidos com autorização; validar os indicadores antes de decidir.'}
    except (ValueError,TypeError,AttributeError) as exc:
        raise REBError('Resposta HubSpot inesperada') from exc
