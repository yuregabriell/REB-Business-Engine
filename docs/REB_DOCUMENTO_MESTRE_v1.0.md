# REB — Documento Mestre de Arquitetura e Produto

**Nome:** REB — Reverse Engineering Business  
**Subtítulo:** Adaptive Business Intelligence, Execution & Mentorship  
**Versão da especificação:** 1.0  
**Data:** 19 de outubro de 2026  
**Situação:** desenho e requisitos acordados em conversa. O produto completo **ainda não foi desenvolvido, instalado ou testado**.

> **Missão:** dar a pessoas com qualquer nível de experiência acesso a uma equipa coordenada de inteligência empresarial que ajude a transformar ideias em operações viáveis, compreender e adaptar modelos de negócio existentes, melhorar empresas em funcionamento e desenvolver competências do próprio empreendedor.
>
> **Limite essencial:** o REB deve procurar aumentar a probabilidade de boas decisões e de resultados sustentáveis, **não prometer nem garantir sucesso financeiro**.

## 1. Visão e pilares

O REB vai além da engenharia reversa tradicional. Tem duas capacidades complementares:

1. **Business Reverse Engineering (BRE):** estudar um negócio existente, documentar o que é publicamente observável, inferir com prudência o modelo comercial, financeiro e operacional, e ajudar a conceber uma empresa concorrente com execução e diferenciação próprias.
2. **Business Success Engine (BSE):** partir de uma ideia, um problema, um negócio em lançamento ou uma operação madura para investigar, validar, executar, medir, corrigir e crescer.

O resultado esperado não é somente um relatório; é uma sequência de decisões e ações acompanhadas por evidências verificáveis. O REB deve saber recomendar prosseguir, ajustar, testar outra hipótese ou não investir.

## 2. Perfis de utilizadores

- **Iniciante absoluto:** só tem uma ideia (por vezes vaga), poucos recursos ou nenhuma experiência. Recebe explicações acessíveis e ações de baixo risco, passo a passo.
- **Empreendedor em validação/lançamento:** precisa de descobrir clientes, testar ofertas, fixar preços, construir a primeira operação e concretizar vendas.
- **Empresário com operação existente:** procura solucionar problemas em vendas, margens, entrega, contratação, retenção e processos.
- **Gestor/investidor/empresário avançado:** necessita de análises técnicas, unit economics, projeções, estruturação, otimização e expansão.

O utilizador pode ser avançado numa área e iniciante noutra. A IA adapta o vocabulário, explicação, profundidade e apoio por competência e contexto, mas nunca reduz os padrões de segurança ou aprovação.

## 3. Objetivos do produto e princípios inegociáveis

1. **Evidência antes da convicção:** separar dados verificados, hipóteses, estimativas e lacunas.
2. **Ação mensurável:** cada recomendação importante indica porquê, como, custo aproximado, risco e como avaliar o resultado.
3. **Autonomia proporcional:** investigar e preparar com autonomia; pedir confirmação para enviar mensagens, gastar dinheiro, publicar, contratar, modificar sistemas ou atuar sobre terceiros.
4. **Iniciativa proativa, mas não intrusiva:** identificar a próxima decisão útil, sem substituir escolhas do utilizador.
5. **Baixo custo antes de alto custo:** testar alternativas frugais e impor portas de investimento (Investment Gates).
6. **Ceticismo construtivo:** ter um auditor interno que procure cenários negativos e contraprovas.
7. **Mentoria adaptativa:** fazer o conhecimento crescer junto com o negócio.
8. **Portabilidade:** skill para agentes existentes; motor e armazenamento próprios quando necessário; adaptações para MCP/A2A e interfaces independentes.
9. **Legalidade e privacidade:** respeitar propriedade intelectual, termos de utilização, RGPD e normas locais.
10. **Memória explícita e corrigível:** decisões, evidências e métricas persistentes; o utilizador consegue revê-las e corrigir premissas.

## 4. Modos de funcionamento

### Modo A — Da ideia ao negócio
Inicia com a ideia, local de operação, orçamento, recursos, capacidades e objetivo. Pesquisa alternativas, seleciona hipóteses de maior risco, propõe testes, cria oferta inicial, acompanha vendas e operação.

### Modo B — Engenharia reversa de um negócio
Inicia com empresa, URL, mercado, marca ou modelo. Identifica oferta, preços públicos, clientes, canais, diferenciação, operação provável, regras legais e economia estimada. Constrói *blueprint* independente, com informação confirmada versus inferida.

### Modo C — Diagnóstico e melhoria
Inicia com empresa já existente, sintomas e dados reais fornecidos/ligados. Audita indicadores, encontra gargalos, prioriza intervenções, executa experiências autorizadas e acompanha resultados.

### Modo D — Estratégia avançada e expansão
Trabalha portfólio, novas regiões, margens por segmento, cenários, investimento, escalabilidade e trade-offs.

### Modo E — Mentoria e evolução
Corre transversalmente aos modos, adaptando explicações, desafios e aprendizagem na execução real.

## 5. Os 14 especialistas do REB

Os 12 agentes operacionais acordados, mais 2 agentes transversais:

| ID | Agente | Missão | Saídas fundamentais |
|---|---|---|---|
| A01 | **CEO / Orquestrador** | Interpretar objetivo, escolher especialistas, ordenar hipóteses e acompanhar decisões | plano de trabalho, prioridades, decisões pendentes |
| A02 | **Investigador de Mercado** | Concorrência, procura, benchmarking, pesquisa setorial e reversa empresarial | mapa de mercado, concorrentes, fontes, gaps |
| A03 | **Especialista em Clientes** | Identificar segmentos, dores, comportamento, compra e retenção | personas hipóteses, entrevistas, mapa de necessidades |
| A04 | **Validador de Negócios** | Criar e interpretar experiências comerciais | hipóteses, teste, critérios, evidências, decisão |
| A05 | **Diretor Financeiro** | Custos, preços, margem, caixa, orçamento, cenários | modelo financeiro, ponto de equilíbrio, riscos |
| A06 | **Arquiteto de Ofertas** | Definir proposta de valor, pacotes, preço e diferenciação | catálogo de oferta e argumentos de venda |
| A07 | **Diretor de Operações** | Processos, fornecedores, logística, equipas, qualidade e infraestrutura | SOPs, plano operacional, capacidade e custos |
| A08 | **Especialista Regulatório** | Pesquisar licenças, obrigações, privacidade, contratos e conformidade | checklist jurídica para validação por especialistas |
| A09 | **Diretor de Marketing** | Posicionamento, canais, conteúdo e testes de aquisição | estratégia de canais, briefs, experiências |
| A10 | **Diretor Comercial** | Prospecção, propostas, CRM, acompanhamento e negociação | funil comercial, scripts, tarefas e métricas |
| A11 | **Analista de Crescimento** | Medir aquisição, conversão, margens, retenção e eficiência | painel de KPIs, análises e melhoria contínua |
| A12 | **Auditor Estratégico** | Contestar pressupostos, auditar cálculos/fontes e detetar falhas | relatório de contraprovas, risco, confiança |
| A13 | **Knowledge Scientist** | Investigar e avaliar conhecimento de estudos, livros e casos reais | fichas de métodos, grau de evidência e aplicabilidade |
| A14 | **Evolution Mentor** | Adaptar vocabulário e desenvolver competências e autonomia | perfil por competência, explicações e desafios |

Não é necessário executar 14 modelos simultâneos. Um orquestrador invoca os agentes relevantes e partilha artefactos. O **Nexus** e o **Executor** são camadas técnicas de coordenação e ação, não especialistas adicionais que trabalham continuamente.

## 6. REB Nexus — conector de skills, ferramentas e agentes

**Objetivo:** permitir que o REB descubra capacidades externas, delegue trabalhos e aproveite resultados sem obrigar o utilizador a gerir manualmente vários agentes.

- **Agent Skills:** instruções e métodos instaláveis, lidos pelo agente hospedeiro; não são por si só agentes autónomos.
- **MCP:** ferramentas e acesso a fontes/sistemas externos; útil para REA e aplicações empresariais.
- **A2A:** delegação entre agentes independentes quando ambos oferecem essa interface; não substituir MCP por A2A sem necessidade.
- **Adaptadores internos:** CLI, HTTP/API, ficheiros e tarefas conforme as capacidades de cada sistema.
- **Permissões e observabilidade:** escopo de acesso, autenticação, estado, identificador de tarefa, limite de custos, registo de ações e gestão de erros.

**Integração REA:** para investigar o comportamento e funcionalidades de aplicações autorizadas; devolve evidências e dados técnicos, não uma reprodução mágica e perfeita.

**Integração RES:** para mapear fluxos, requisitos e funcionamento observável de SaaS; devolve documentação e especificações. Se o objetivo for implementar código, um agente construtor ou ferramenta de desenvolvimento executa a implementação.

**Integrações empresariais opcionais:** motores de pesquisa e extração (Firecrawl/Crawl4AI, respeitando limites), Similarweb/Ahrefs/G2 (conforme acesso), CRM (HubSpot, etc.), analítica (GA4, PostHog), ferramentas de automação (n8n), vendas e finanças. Ligações reais dependem da instalação, autenticação e permissões de cada fornecedor.

**Exemplo de fluxo:** REB investiga oportunidade → Nexus chama RES para especificação de SaaS e/ou REA para análise de aplicação → REB interpreta relevância e viabilidade → agente de desenvolvimento recebe tarefa aprovada → REB mede resultados e custos.

## 7. Knowledge Scientist e biblioteca de conhecimento

Uma biblioteca **operacional e crítica**, em vez de um repositório de frases motivacionais. Fontes iniciais discutidas:

- **Estudos com controlo/comparação:** formação em iniciativa pessoal de microempresas no Togo; investigação sobre abordagem científica e teste de hipóteses em startups italianas.
- **Casos documentados de fundadores:** Buffer (testes de preço/procura), Airbnb (aprendizagem manual com anfitriões), Dropbox (demonstração para recolher interesse), Superhuman (feedback segmentado e procura do produto).
- **Livros e métodos:** *The Mom Test*, *Testing Business Ideas*, *The Lean Startup*, *Traction*, *High Output Management*.
- **Projetos existentes para auditar antes de reutilizar:** OpenBusiness, Startup Skills, Market Skills e B2B GTM Suite.

**Cada ficha de conhecimento contém:** fonte/data, afirmação original, tipo de evidência, método, população/setor, custo e pré-requisitos, possíveis limitações, falhas conhecidas, contexto onde pode funcionar, intensidade de prova, métricas e formas de testar.

Um caso de sucesso não estabelece automaticamente causalidade. Uma lição transferida de SaaS para comércio local exige adaptação e teste. Respeitar licenças de software e direitos de autor dos livros.

## 8. REB Evolution — mentoria e adaptação de vocabulário

O REB mantém um **mapa de competências por domínio**, não um rótulo único de nível do utilizador:

- fundamentos e visão de negócio;
- finanças e interpretação de indicadores;
- pesquisa de clientes e validação;
- marketing, vendas e negociação;
- operação e liderança;
- estratégia, decisões sob incerteza e autonomia.

Adapta termos, exemplos, quantidade de explicação e exercícios. Introduz conceitos técnicos gradualmente quando forem úteis para decisões reais. O utilizador pode pedir linguagem simples ou análise técnica a qualquer momento.

**Avaliação responsável:** usar competências demonstradas em decisões, exercícios ou ações reais, sem inferir traços pessoais permanentes nem confundir uso frequente com evolução. Mostrar e permitir corrigir o perfil. O sucesso inclui crescente capacidade do utilizador decidir sem depender do sistema.

## 9. Business Journey — diário e avaliação longitudinal

O teste público pretendido pelo utilizador será construir **um negócio real desde uma ideia do zero**, mantendo diário de decisões, experiências e resultados até existir desempenho comercial sustentável (não pressupondo que ocorrerá).

Cada entrada pode registar:

- data e estado do negócio;
- objetivo, hipótese e motivo da decisão;
- recomendação do REB e decisão do utilizador;
- ação executada, responsável e autorizações;
- custo e tempo efetivos;
- potenciais clientes contactados, propostas, vendas e repetição de compra;
- faturação, custos, lucro/margem e fluxo de caixa — mantidos separados;
- fontes e provas de cada resultado;
- erros, aprendizagens, seguinte experiência.

O diário pode gerar relatórios e conteúdos publicáveis apenas mediante aprovação e anonimização quando necessária. São igualmente registados insucessos e decisões de não prosseguir. O diário é parte do motor de avaliação, não ferramenta para fabricar histórias inspiradoras.

## 10. Ciclo central de trabalho

**Entender → Diagnosticar → Investigar → Priorizar hipóteses → Validar → Planear → Executar (com autorização) → Medir → Auditar → Ajustar/Pivotar/Escalar.**

**Antes de investir:** Investment Gate avalia base factual, alternativas mais baratas, necessidades de caixa, perdas máximas admissíveis, cenários otimista/base/pessimista, critérios de interrupção e confirmação expressa.

**Antes de recomendar:** o Auditor verifica contraprovas, fontes, valores e contradições.

**Depois de executar:** indicadores reais substituem estimativas, preservando histórico da versão anterior da hipótese.

## 11. Outputs do REB

- dossiê de modelo de negócio e mapa competitivo;
- canvas de modelo de negócio e proposta de valor;
- ranking justificado de hipóteses e experiências de validação;
- oferta inicial, tabela de preços, argumentário e materiais comerciais;
- planilha financeira de cenários, margens, fluxo de caixa e ponto de equilíbrio;
- plano operacional, fornecedores, equipa, checklists e SOPs;
- calendário de marcos, responsáveis, dependências e orçamento;
- diagnóstico empresarial e plano de melhoria;
- dashboard de indicadores, diário de experiências e aprendizagem;
- documentos e tarefas estruturadas para REA, RES e ferramentas construtoras.

Cada artefacto contém identificação de versão e, quando necessário, fontes e grau de confiança.

## 12. Setores e contextos

**Packs sectoriais modulares**, inicialmente:

- serviços locais (limpeza, manutenção, reparações, etc.);
- SaaS e negócios digitais;
- e-commerce;
- lojas e retalho;
- serviços profissionais e agências;
- logística e serviços de entrega.

Cada pack inclui modelos operacionais, métricas, custos típicos identificados como intervalos aproximados, pesquisa e regulações pertinentes ao país/região. Não presumir que requisitos legais são iguais entre jurisdições. Portugal pode ser primeiro mercado de teste, mas o sistema deve ser internacionalizável.

## 13. Arquitetura lógica

```text
Utilizador (ChatGPT/Claude/Codex/Web/Desktop/Móvel)
                    |
           Interface + autenticação
                    |
         REB Core / CEO Orquestrador
          /         |          \
   Agentes         Nexus      Business Journey
      |              |                |
 Knowledge Base   Skills/MCP/A2A   Projetos/KPIs
      |              |                |
 Evidências       REA/RES/CRM      Eventos/Logs
      \______________|________________/
                    |
       Auditoria + Investment Gates
                    |
         Decisões e ações autorizadas
```

**Distribuição do raciocínio:** skills portáteis que podem usar o modelo IA do hospedeiro. **Funções que precisam de garantias de execução:** scripts determinísticos, base de dados, motor de tarefas, conectores, controle de permissões e memória persistente. **Versão alojada (opcional):** API/servidor e armazenamento central.

## 14. Organização prevista do repositório

```text
reb/
├── README.md
├── LICENSE
├── docs/
│   ├── architecture/
│   ├── product/
│   ├── integration-contracts/
│   └── security/
├── skills/
│   ├── reb-core/SKILL.md
│   ├── business-reverse-engineering/
│   ├── business-validation/
│   ├── market-research/
│   ├── finance/
│   ├── operations/
│   ├── commercial-growth/
│   ├── knowledge-scientist/
│   └── evolution-mentor/
├── agents/
│   ├── manifest.yaml
│   ├── orchestrator/
│   ├── specialists/
│   └── strategic-auditor/
├── knowledge/
│   ├── methods/
│   ├── scientific-studies/
│   ├── founder-cases/
│   ├── counterexamples/
│   └── evidence-schema/
├── industry-packs/
│   ├── local-services/
│   ├── saas/
│   └── ecommerce/
├── nexus/
│   ├── registry/
│   ├── adapters/mcp/
│   ├── adapters/a2a/
│   ├── adapters/rea/
│   ├── adapters/res/
│   └── permissions/
├── engine/
│   ├── workflows/
│   ├── experiments/
│   ├── calculations/
│   ├── investment-gates/
│   ├── evidence/
│   ├── memory/
│   └── evaluations/
├── business-journey/
│   ├── journal/
│   ├── metrics/
│   └── exports/
├── api/
├── ui/
├── mcp-server/
├── cli/
├── examples/
├── tests/
├── deploy/
└── .github/workflows/
```

Estrutura proposta, **não repositório já existente**.

## 15. Contratos internos de agente

Todo agente recebe:

- `project_id`, `task_id`, objetivo, contexto, país/setor, horizonte e orçamento;
- permissões e ferramentas autorizadas;
- evidências disponíveis, hipóteses em aberto e regras de segurança;
- formato de saída e critério para declarar conclusão.

Todo agente devolve:

- `status` (sucesso, parcial, bloqueado, erro);
- conclusões e ações propostas;
- fontes, evidências e sua qualidade;
- custos/risco/limitações;
- perguntas ou dados em falta;
- próximos passos e artefactos gerados.

Ações são idempotentes sempre que possível, auditadas e recuperáveis após falhas. Cálculos financeiros usam código testado, não apenas geração textual.

## 16. Segurança, ética e conformidade

- Não se apresentar como capaz de garantir êxito nem como substituto automático de contabilistas, advogados e consultores licenciados.
- Não copiar propriedade intelectual protegida, dados pessoais, credenciais, segredos comerciais ou contornar controlo de acesso em estudos de concorrentes.
- Respeitar privacidade, RGPD, consentimentos, termos de APIs e websites.
- Pedir aprovação explícita para mensagens a terceiros, compras, publicações, alterações de preços/campanhas e execuções com impacto financeiro.
- Guardar o mínimo de dados pessoais necessários, com perfis de acesso, retenção e eliminação definidos.
- Assinalar números não verificados, conflitos de fontes e estimativas sensíveis.
- Monitorizar custos de API, scraping, pesquisa e execução para não consumir orçamento sem autorização.

## 17. Modelo de instalação e distribuição

**Inspirado no RES:** uma **skill principal** de agente instalável em repositórios ou globalmente para ambientes compatíveis, mais skills sectoriais e de especialistas. Não requer modelo de IA próprio.

**Inspirado no REA:** um `reb setup` (a construir) poderia configurar skills e ferramentas MCP para Codex/Claude/Cursor ou outros ambientes suportados.

**Para ChatGPT:** desenvolver e alojar um servidor MCP remoto próprio quando necessário; instalar a skill num repositório GitHub **não** a torna automaticamente acessível às conversas ChatGPT.

**Versão autónoma futura:** serviço API e interfaces Web, Windows/macOS/Linux e Android, ligados ao mesmo motor. Docker pode facilitar self-hosting. Não é necessário lançar todas as interfaces na primeira versão.

**Distribuição GitHub:** código-fonte, releases versionadas, instalador CLI e, quando disponíveis, executáveis/APK reais e CI de builds. Evitar afirmar que APK e instalador estão prontos antes de os compilar e testar.

## 18. Estratégia de implementação por etapas

**Etapa 0 — Especificação e validação de dependências:** contratos, licenças, segurança, mecanismos de avaliação e escolha de bibliotecas.

**Etapa 1 — Núcleo inteligente instalável:** skill principal, orquestrador, agentes de investigação/validação/finanças/operação/auditoria, modelo comum de evidências, project store e CLI de setup.

**Etapa 2 — Conhecimento científico:** Knowledge Scientist, fichas rigorosas, mecanismos de atualização e testes que distinguem estudos, relatos e inferências.

**Etapa 3 — Execução e medição:** Business Journey, motor de experimentos, métricas, gates financeiros, relatórios e acompanhamento longitudinal.

**Etapa 4 — Interoperabilidade:** Nexus, descoberta de ferramentas, adaptadores MCP REA/RES, contratos de integração, permissões e recuperação de erros.

**Etapa 5 — Experiência avançada:** Evolution Mentor, adaptação por competências, packs sectoriais, análises avançadas e fluxos para negócios maduros.

**Etapa 6 — Distribuição ampla:** plugin ChatGPT via MCP remoto, portal e eventualmente apps instaláveis. Testes de acessibilidade, autenticação e custos.

A ordem pode ser revista, mas o sistema deve ser desenhado desde o início como um único produto evolutivo, não como protótipos incompatíveis.

## 19. Testes de aceitação — definição de 'pronto'

O REB só deve ser descrito como pronto para um teste real exigente quando conseguir:

1. Receber ideia vaga e formular passos sem inventar contexto.
2. Comparar alternativas e identificar custo/risco/cliente-alvo.
3. Pesquisar concorrentes e citar fontes de forma rastreável.
4. Separar evidências de hipóteses e desconhecidos.
5. Criar experiências com critérios verificáveis e limites de perda.
6. Calcular preço, margem, ponto de equilíbrio e cenários com testes automatizados.
7. Reconhecer contextos legais e solicitar revisão humana quando necessário.
8. Coordenar especialistas sem perder contexto nem contradizer resultados.
9. Conectar pelo menos uma ferramenta externa em ambiente de testes e tratar falhas.
10. Registar memória, decisões, despesas e resultados entre sessões.
11. Adaptar a linguagem sem subestimar ou sobrecarregar o utilizador.
12. Recusar conclusões categóricas quando faltam dados.
13. Exportar projeto completo e diário de atividades.
14. Exigir aprovação para ações que gastam dinheiro, enviam mensagens ou modificam sistemas.
15. Mostrar, em ensaios repetidos, utilidade superior a gerar um relatório genérico.

**Critério de resultado real:** avanços demonstrados em métricas do negócio e competências do utilizador, sem prometer um desfecho positivo. Avaliar também falhas, abandonos, custo de ferramentas e tempo do utilizador.

## 20. Métricas de desempenho do REB

**Negócio:** procura validada, clientes pagos, retenção/recompra, vendas, margem, caixa, taxa de conversão, custo de aquisição, produtividade, satisfação.

**Qualidade do agente:** precisão dos factos, cobertura de fontes, erros financeiros, taxa de tarefas concluídas, reversões após nova evidência, transparência, custo por análise.

**Capacitação:** competência demonstrada ao interpretar indicadores, qualidade de decisões independentes, compreensão de riscos, autonomia progressiva.

As métricas são escolhidas segundo o tipo e a fase do negócio; não há um score único universal que prove 'sucesso'.

## 21. O que está definido, o que existe e o que falta

### Definido nesta conversa
- Missão dupla: reconstrução de modelos empresariais e assistência contínua a resultados.
- Quatro perfis de utilização + mentoria adaptativa.
- 14 especialistas (12 operacionais + Knowledge Scientist + Evolution Mentor).
- Nexus para skills, MCP, REA, RES e outros agentes.
- Business Journey, biblioteca de evidências e Investment Gate.
- Distribuição prioritária como skill portável, com extensões MCP e interfaces opcionais.
- Teste real com ideia criada do zero e diário documentado.

### Recursos existentes fora do REB
- REA e RES são projetos externos com métodos de instalação e integração a verificar na versão escolhida.
- OpenBusiness e outros frameworks/skills são candidatos a referência ou reutilização, sujeitos a auditoria de licença e funcionamento.
- Similarweb foi ligado ao ChatGPT durante a conversa; **isso não equivale a uma integração instalada no futuro REB**.

### Ainda por implementar
- Repositório, código, skills próprias, MCP, Nexus, base de dados, ensaios, documentação técnica final, CLI, plugin, aplicativos e integração real com REA/RES.
- Validação atualizada das fontes de investigação, licenças, custos e compatibilidade entre ferramentas.
- Planeamento operacional do teste longitudinal e definição de critérios mensuráveis.

## 22. Próxima decisão de engenharia

Iniciar pelo **contrato de agentes**, **formato de evidências** e **especificação de tarefas do REB Core**. Estes três elementos serão a fundação sobre a qual as skills, o Knowledge Scientist, Nexus, os modelos financeiros e o Business Journey poderão crescer sem reescritas frequentes.

---

**Documento de referência do projeto — versão 1.0.** Mudanças futuras devem ser registadas com versão, motivo, impacto e estado de implementação.
