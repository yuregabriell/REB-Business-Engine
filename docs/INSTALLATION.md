# REB installation — CLI, Studio and Agent Skills

## Environment

Use Python 3.11 or newer. Clone/extract the repository. On a fresh networked machine:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
reb doctor
```

## Local REB Studio

`reb studio` and open `http://127.0.0.1:8765`. This local UI requires no cloud subscription for local storage, deterministic financial scenarios or logging.

## CLI

`reb init "Nome" "Ideia" --budget 250 --market Portugal`; `reb projects` then `reb diagnose PROJECT_ID`.

## Agent Skills

In the source checkout: `python scripts/install_skills.py --host codex` or `--host claude`, `--host cursor`, `--host project`. `--dry-run` previews destinations. Existing skill files are not overwritten unless `--force`.

## MCP host

MCP stdio: `reb-mcp`. For desktop hosts, replace command with the full executable path from `which reb-mcp` / `where reb-mcp` if PATH is not inherited. The included `.mcp.json` is a generic starting point; host-specific settings differ. An OpenAI ChatGPT remote plugin needs an independent HTTPS remote MCP service and OAuth, which is not included yet.

## AI and web search providers

Set `REB_MODEL_BASE_URL`, `REB_MODEL_API_KEY`, `REB_MODEL` to enable `reb ask` and `reb mission`. Set `TAVILY_API_KEY` for `reb research`. Defaults are offline and never invent sourced research results. Your API vendor may charge; never commit the values.

## Publication via GitHub CLI

With an authenticated local `gh`, run `bash scripts/publish-github.sh OWNER private` on an unpushed repository to create a *separate* `OWNER/reb-business-engine` repository. No Github CLI token is included in this archive.

## Development

`python -m pip install -e '.[test]' && python -m pytest`
