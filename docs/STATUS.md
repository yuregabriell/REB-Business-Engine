# Estado — REB 0.2.0 (20/10/2026)

## Implementado e verificado localmente

- 14 perfis de especialista, seleção contextual, skills instaláveis e orquestração sequencial **quando** uma API de IA compatível é configurada.
- Memória SQLite local: projetos, evidências, experimentos, diário, demonstrações de aprendizagem e recibos resumidos de delegações.
- Motor financeiro decimal com ponto de equilíbrio e gate de autorização (a decisão do REB não transfere dinheiro).
- Biblioteca original de seis fichas de métodos, com fonte, nível de evidência, procedimento, métrica, ressalvas.
- Blueprint determinístico por etapa, ancorado no conteúdo efetivamente registado (não simula pesquisa ou execução).
- Descoberta opcional via Tavily; resultados são **sempre** registados como *unverified* até revisão humana da fonte.
- Nexus MCP **cliente** stdio: inicia servidor autorizado em configuração local, handshake, lista ferramentas, executa ferramentas listadas e autorizadas, aplica permissões explícitas de leitura/escrita, com timeout e recibos resumidos opcionais no projeto.
- Servidor MCP **REB** stdio: ferramentas internas, incluindo os novos métodos, blueprint e pesquisa opcional.
- REB Studio (web local) com plano de ação, lista de métodos, finanças, evidências, experiências, diário e projetos; verificação de Host, token anti-CSRF e binding loopback.
- Testes de integração do cliente Nexus contra um **servidor MCP de teste** (não REA real), testes de segurança e regressões da versão anterior.

## Não está implementado ou não está validado

1. Publicação no GitHub e permissões para **criar repositório**: o conector disponível permite operações em repositórios existentes, não criação de novo. Um proprietário pode criar repositório vazio e depois permitir publicação.
2. Integração REA **real**: configurar o comando exato do seu servidor MCP; auditar catálogo de ferramentas e autorizar apenas as necessárias; testar comportamento com aplicações autorizadas. Não incluir exemplos de comandos de inicialização do REA sem confirmação.
3. RES: skill não é necessariamente MCP; depende de host compatível ou adaptador de agente remoto. Não foi testado.
4. Servidor remoto HTTPS MCP OAuth para ChatGPT `@REB`: **não implementado**. Servidor atual é stdio local.
5. A2A, CRM e fornecedores reais: dependem de cada API, autenticação, licença e homologação.
6. Busca web turnkey sem chaves: Tavily exige chave configurada pelo operador; pesquisas externas não foram feitas nos testes locais.
7. Modelo de IA turnkey: requer base URL, chave e nome de modelo; o motor determinístico funciona offline.
8. Verificação automática independente de fontes, resultados financeiros de terceiros, licenciamento local e aconselhamento jurídico: **não disponíveis**.
9. Alojamento multiutilizador, segurança cloud, monitorização operacional, encriptação avançada e isolamento por cliente.
10. Aplicação nativa Android/Windows, sincronização de dispositivos, publicação de campanhas, operações comerciais externas autónomas e resultados reais de clientes.

## Próximos trabalhos prioritários

- End-to-end contra REA numa instalação de teste autorizada; adaptar schemas e limites de recursos.
- Host dedicado para RES ou ponte com agente de skill instalado.
- Melhorar estrutura dos resultados dos especialistas e auditoria de evidências.
- Serviço remoto MCP autenticado e isolamento por utilizador, com testes de segurança.
- Aumentar os métodos documentados com bibliografia e estudos reproduzíveis, sujeitos a revisão humana.
- Integrar fornecedores de pesquisa, CRM, análises e contabilidade com consentimento.
- Pilotos reais com diário de receitas, custos, clientes, erros e evolução de competências.

**Aviso:** funcionalidade técnica não constitui garantia de sucesso comercial nem prova de eficácia do REB em negócios reais.
