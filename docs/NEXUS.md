# REB Nexus — comunicação real via MCP stdio

O Nexus contém um cliente MCP stdio opt-in. `reb delegate` continua a criar apenas uma proposta de delegação, enquanto `reb nexus-call` **executa** uma chamada real a uma ferramenta externa pré-configurada, após autorização explícita do utilizador.

## Configuração segura

1. Instale o servidor MCP pretendido e confirme **o comando real de lançamento do fornecedor** na documentação respetiva.
2. Copie `examples/nexus-config.example.json` para um ficheiro local e substitua o caminho exemplificativo do REA pelo comando verdadeiro; não utilize `shell`, pipes ou comandos concatenados.
3. `allowed_tools` começa vazio, bloqueando qualquer execução. Liste ferramentas e acrescente apenas os nomes e níveis `read` / `write` necessários:

```bash
reb nexus-tools rea --config ./nexus-local.json
reb nexus-call rea nome_real_da_tool --config ./nexus-local.json \
  --args '{"target":"alvo_autorizado"}' --approve-external
```

Para ferramentas com efeitos externos é obrigatória uma **segunda** confirmação `--approve-write` e declaração `"nome_real_da_tool":"write"` no allowlist. Não forneça credenciais na linha de comando; use armazenamento seguro de secrets/variáveis do processo.

Para registar um **recibo sem o conteúdo potencialmente sensível** no diário do projeto, acrescente `--project-id ID`. O recibo contém o fornecedor, ferramenta, nomes dos campos enviados, estado e tipos de conteúdo do resultado, mas **não** regista valores e texto devolvido. Os valores do resultado são apresentados na sessão ao operador e podem incluir informação privada: proteja os logs do terminal.

## Sem promessas automáticas

- MCP local ≠ plugin remoto ChatGPT. Será necessário servidor HTTPS e autenticação adequada.
- A skill RES não é um servidor MCP automaticamente; precisa de um agente/host que a execute ou de outro adaptador.
- O comando placeholder de REA no exemplo **não é executável** até o operador o substituir.
- Os resultados externos não passam automaticamente a ser factos verificados.
- O allowlist protege a superfície de ferramentas, mas **não** é um sandbox do processo executável; instale somente servidores de confiança e use permissões mínimas.
- Cada execução abre uma nova sessão, com timeout. Tarefas assíncronas de longa duração e protocolos A2A serão componentes diferentes.
