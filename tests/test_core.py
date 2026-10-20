import json
import os
import subprocess
import sys
from pathlib import Path
from decimal import Decimal
import pytest
from reb.storage import Store
from reb.errors import REBError, MissingProvider
from reb.finance import financial_scenario, investment_gate, money
from reb.engine import diagnose, recommend_experiment, spending_review
from reb.evolution import adaptive_explanation, skill_profile
from reb.agents import AGENTS, select_agents
from reb.nexus import CAPABILITIES, make_delegation, discover_skills
from reb.mcp_stdio import dispatch, TOOLS

@pytest.fixture
def store(tmp_path):
    with Store(tmp_path / 'projects.db') as s:
        yield s

@pytest.fixture
def project(store):
    return store.add_project('Lavandaria', 'Recolha e entrega de roupa', budget='300')

def test_projects_persist(tmp_path):
    path = tmp_path / 'data.db'
    with Store(path) as s: pid = s.add_project('A', 'Uma ideia')['id']
    with Store(path) as s: assert s.get_project(pid)['idea'] == 'Uma ideia'

def test_invalid_project_and_sql_injection(store):
    with pytest.raises(REBError): store.add_project('', 'ideia')
    with pytest.raises(REBError): store.add_project('a', 'b', stage='fake')
    with pytest.raises(REBError): store.get_project("' OR 1=1 --")

def test_source_verification_requires_url(store, project):
    with pytest.raises(REBError): store.add_evidence(project['id'], 'demanda comprovada', status='verified')
    with pytest.raises(REBError): store.add_evidence(project['id'], 'foo', url='javascript:alert(1)')
    v = store.add_evidence(project['id'], 'site oficial existe', url='https://example.org/', status='verified')
    assert v['status'] == 'verified'

def test_experiment_lifecycle(store, project):
    x = store.add_experiment(project['id'], 'procura paga', 'pedidos', '3', '20')
    assert store.experiments(project['id'])[0]['state'] == 'planned'
    new = store.set_experiment_result(x['id'], '3 pagamentos', 'completed')
    assert new['state'] == 'completed'
    with pytest.raises(REBError): store.set_experiment_result(x['id'], '', 'completed')

def test_journal_revenue_and_profit(store, project):
    store.add_journal(project['id'], 'primeira venda', revenue='100', cost='75', customers=1)
    d = diagnose(store, project['id'])
    assert d['journal_totals']['net_recorded'] == '25'
    assert d['journal_totals']['revenue_recorded'] == '100'
    assert d['success_guarantee'] is False

def test_journal_rejects_invalid_data(store, project):
    with pytest.raises(REBError): store.add_journal(project['id'], 'teste', revenue='NaN')
    with pytest.raises(REBError): store.add_journal(project['id'], 'teste', customers=-1)

def test_financial_breakeven():
    f = financial_scenario('40', '12', '200', 10, cash='800', customer_acquisition_cost='3')
    assert f['revenue'] == '400'
    assert f['total_cost'] == '350'
    assert f['operating_result'] == '50'
    assert f['breakeven_units'] == 8
    assert f['runway_periods_without_sales'] == '4.00'

def test_financial_negative_margin():
    f = financial_scenario('10', '15', '100', 20)
    assert f['breakeven_units'] is None
    assert f['operating_result'] == '-200'

def test_finance_decimal_accuracy():
    f = financial_scenario('0.30', '0.20', '0', 3)
    assert f['operating_result'] == '0.30'
    with pytest.raises(REBError): money('Infinity')
    with pytest.raises(REBError): financial_scenario('1', '0', '1', -1)

def test_investment_gate(store, project):
    d = spending_review(store, project['id'], '100')
    assert d['allowed'] is False
    assert any('autorização' in x for x in d['reasons'])
    store.add_evidence(project['id'], 'Fonte disponível', 'https://example.org', 'verified')
    assert spending_review(store, project['id'], '100', approved=True)['allowed']
    assert not spending_review(store, project['id'], '1000', approved=True)['allowed']

def test_learning_profile(store, project):
    pid = project['id']
    assert skill_profile(store,pid)['levels']['finance'] == 0
    store.add_learning(pid, 'finance', 2, 'Calculou margem sem ajuda')
    assert skill_profile(store,pid)['levels']['finance'] == 2
    assert 'margem' in adaptive_explanation('finance', 2)['explanation'].lower()
    with pytest.raises(REBError): store.add_learning(pid, 'finance', 5, 'lido livro')

def test_all_agents_present():
    assert len(AGENTS) == 14
    assert len({x.key for x in AGENTS}) == 14
    assert any(x['key'] == 'auditor' for x in select_agents('idea'))
    assert any(x['key'] == 'regulatory' for x in select_agents('idea', 'regras e impostos'))

def test_nexus_does_not_fake_execution():
    x = make_delegation('rea','Analisar aplicação autorizada')
    assert x['execution_status'] == 'prepared_not_executed'
    assert x['requires_explicit_approval']
    with pytest.raises(REBError): make_delegation('bad', 'task')

def test_nexus_skills_discovery(tmp_path):
    (tmp_path/'reb-core').mkdir()
    (tmp_path/'reb-core'/'SKILL.md').write_text('---\nname: reb-core\n---')
    assert len(discover_skills(tmp_path)) == 1

def test_export_contains_history(store, project):
    assert set(store.export(project['id'])) == {'project','evidence','experiments','journal','learning','delegations'}

def test_mcp_initialize_and_tools(store):
    init = dispatch({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05'}},store)
    assert init['result']['serverInfo']['name'] == 'reb-business-engine'
    listing = dispatch({'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},store)
    assert len(listing['result']['tools']) == len(TOOLS)
    assert dispatch({'jsonrpc':'2.0','method':'notifications/initialized'},store) is None

def test_mcp_tool_calls(store):
    response = dispatch({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'reb_create_project','arguments':{'name':'X','idea':'Y'}}},store)
    assert not response['result']['isError']
    pid = json.loads(response['result']['content'][0]['text'])['id']
    result = dispatch({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'reb_diagnose','arguments':{'project_id':pid}}},store)
    assert 'next_actions' in json.loads(result['result']['content'][0]['text'])
    bad = dispatch({'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'not_a_tool','arguments':{}}},store)
    assert bad['result']['isError']

def test_cli_end_to_end(tmp_path):
    env={**os.environ, 'REB_DB_PATH':str(tmp_path/'reb.db')}
    p=subprocess.run([sys.executable,'-m','reb.cli','init','Lavandaria','Lavagem local','--budget','300'],env=env,capture_output=True,text=True)
    assert p.returncode == 0, p.stderr
    pid=json.loads(p.stdout)['id']
    d=subprocess.run([sys.executable,'-m','reb.cli','diagnose',pid],env=env,capture_output=True,text=True)
    assert d.returncode == 0
    assert json.loads(d.stdout)['project']['id'] == pid

def test_mcp_stdio_subprocess(tmp_path):
    env={**os.environ, 'REB_DB_PATH':str(tmp_path/'mcp.db')}
    inp='\n'.join([json.dumps(x) for x in [
        {'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},
        {'jsonrpc':'2.0','method':'notifications/initialized'},
        {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}}]])+'\n'
    out=subprocess.run([sys.executable,'-m','reb.mcp_stdio'],input=inp,capture_output=True,text=True,env=env,timeout=10)
    assert out.returncode == 0, out.stderr
    lines=[json.loads(x) for x in out.stdout.splitlines()]
    assert len(lines)==2
    assert lines[1]['result']['tools']

def test_optional_model_requires_config(monkeypatch):
    from reb.provider import model_config
    for k in ('REB_MODEL_API_KEY','REB_MODEL_BASE_URL','REB_MODEL'):
        monkeypatch.delenv(k,raising=False)
    with pytest.raises(MissingProvider): model_config()

def test_mission_selects_auditor_last(monkeypatch,store,project):
    from reb import mission
    monkeypatch.setattr(mission,'model_config', lambda: {'configured':True})
    def fake(agent, task, context):
        return {'agent':agent,'content':'Teste: dados não verificados.','status':'draft_not_verified'}
    monkeypatch.setattr(mission,'consult_agent',fake)
    result=mission.run_mission(store,project['id'],'Validar serviço',4)
    assert result['agents_consulted'][0] == 'orchestrator'
    assert result['agents_consulted'][-1] == 'auditor'
    assert len(result['reports']) == 4
    assert result['state'] == 'draft_requires_evidence_validation'


def test_mission_missing_model_fails_before_calls(monkeypatch,store,project):
    from reb import mission
    def missing(): raise MissingProvider('API não configurada')
    monkeypatch.setattr(mission,'model_config',missing)
    with pytest.raises(MissingProvider): mission.run_mission(store,project['id'],'Analisar mercado')


def test_studio_local_api_and_csrf(tmp_path):
    import threading
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    from http.server import ThreadingHTTPServer
    from reb.studio import build_handler
    db=tmp_path/'studio.sqlite3'
    server=ThreadingHTTPServer(('127.0.0.1',0),build_handler(db))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        base=f'http://127.0.0.1:{server.server_port}'
        with urlopen(base+'/') as x: assert b'REB Studio' in x.read()
        with urlopen(base+'/api/session') as x: token=json.load(x)['csrf']
        request=Request(base+'/api/projects',data=json.dumps({'name':'Teste','idea':'Aplicar nova ideia'}).encode(),headers={'Content-Type':'application/json','X-REB-Token':token},method='POST')
        with urlopen(request) as x: assert json.load(x)['name']=='Teste'
        with urlopen(base+'/api/projects') as x: assert len(json.load(x)) == 1
        with pytest.raises(HTTPError) as ex:
            urlopen(Request(base+'/api/projects',data=b'{}',headers={'Content-Type':'application/json'},method='POST'))
        assert ex.value.code == 403
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_installer_no_overwrite(tmp_path):
    import importlib.util
    script=Path(__file__).parents[1]/'scripts/install_skills.py'
    spec=importlib.util.spec_from_file_location('skillinstaller',script)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    first=mod.install(tmp_path)
    assert len(first)==15
    assert (tmp_path/'reb-core'/'SKILL.md').exists()
    second=mod.install(tmp_path)
    assert all(x['state']=='skipped_existing' for x in second)
