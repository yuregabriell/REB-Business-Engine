"""Opt-in, allowlisted MCP stdio connection to external tools (e.g. REA).

No shell execution. Only commands specified by the local operator are launched.
External tools are NEVER auto-approved by an LLM. The CLI requires approval flags.
"""
from __future__ import annotations
import json
import os
import queue
import subprocess
import threading
from pathlib import Path
from .errors import REBError

MAX_MESSAGE = 2_000_000


def read_configuration(config_path: str | Path) -> dict:
    path = Path(config_path).expanduser()
    if not path.is_file():
        raise REBError("Configuração Nexus ausente. Veja examples/nexus-config.example.json")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise REBError("Configuração Nexus inválida") from exc
    if not isinstance(obj, dict) or not isinstance(obj.get("servers"), dict):
        raise REBError("Configuração necessita de 'servers' (objeto)")
    for name, conf in obj["servers"].items():
        if not isinstance(name, str) or not isinstance(conf, dict):
            raise REBError("Servidor inválido")
        cmd = conf.get("command")
        if not isinstance(cmd, list) or not cmd or not all(isinstance(x, str) and x and '\x00' not in x for x in cmd):
            raise REBError("'command' deve ser lista explícita de argumentos; não usar shell")
        allow = conf.get("allowed_tools", {})
        if not isinstance(allow, dict) or any(v not in ("read", "write") for v in allow.values()):
            raise REBError("allowed_tools precisa mapear nomes para 'read' ou 'write'")
        if any(not isinstance(k, str) or not k for k in allow):
            raise REBError("Nomes de ferramentas inválidos")
    return obj


class MCPStdioClient:
    """One bounded session; assumes trusted operator-supplied binary, untrusted responses."""
    def __init__(self, command: list[str], timeout: float = 15, env: dict | None = None):
        if not 0.5 <= timeout <= 120:
            raise REBError("Timeout Nexus fora de intervalo")
        self.command, self.timeout, self.env = command, timeout, env
        self.proc = None
        self.incoming = queue.Queue()

    def __enter__(self):
        try:
            # Child inherits env only from machine + keys explicitly configured by operator.
            self.proc = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL, text=True, bufsize=1, env=self.env)
        except (OSError, ValueError) as exc:
            raise REBError("Não foi possível iniciar o servidor MCP configurado") from exc
        def reader():
            try:
                while True:
                    line = self.proc.stdout.readline(MAX_MESSAGE + 1)
                    if not line:
                        break
                    if len(line) > MAX_MESSAGE:
                        self.incoming.put(REBError("Resposta MCP demasiado grande")); return
                    self.incoming.put(line)
            except (OSError, UnicodeError) as exc:
                self.incoming.put(REBError("Leitura MCP falhou"))
            finally:
                self.incoming.put(None)
        threading.Thread(target=reader, daemon=True).start()
        try:
            self.request("initialize", {"protocolVersion":"2024-11-05", "capabilities":{}, "clientInfo":{"name":"REB Nexus", "version":"0.2.0"}})
            self.notify("notifications/initialized")
        except Exception:
            self.__exit__(None, None, None)
            raise
        return self

    def notify(self, method: str):
        self._send({"jsonrpc": "2.0", "method": method})

    def _send(self, obj):
        if not self.proc or self.proc.poll() is not None:
            raise REBError("Servidor MCP não está ativo")
        try:
            self.proc.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise REBError("Erro ao comunicar com servidor MCP") from exc

    def request(self, method, params=None):
        from time import monotonic
        rid = 1 if method == "initialize" else 2 if method == "tools/list" else 3
        self._send({"jsonrpc":"2.0", "id":rid, "method":method, "params":params or {}})
        deadline = monotonic() + self.timeout
        while True:
            try:
                raw = self.incoming.get(timeout=max(0.01, deadline-monotonic()))
            except queue.Empty:
                raise REBError("Timeout do servidor MCP") from None
            if raw is None:
                raise REBError("Servidor MCP terminou sem resposta")
            if isinstance(raw, Exception):
                raise raw
            try:
                data = json.loads(raw)
            except ValueError:
                raise REBError("Resposta JSON MCP inválida") from None
            if data.get("id") != rid:
                if monotonic() >= deadline:
                    raise REBError("Timeout do servidor MCP")
                continue
            if "error" in data:
                raise REBError("Erro MCP remoto: " + str(data["error"].get("message", "unknown"))[:200])
            if "result" not in data:
                raise REBError("Resultado MCP ausente")
            return data["result"]

    def list_tools(self):
        data = self.request("tools/list")
        return data.get("tools", [])

    def call_tool(self, name, arguments):
        return self.request("tools/call", {"name": name, "arguments": arguments})

    def __exit__(self, exc_type, exc, tb):
        if self.proc is not None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                self.proc.kill()
                self.proc.wait(timeout=2)
            for f in (self.proc.stdin, self.proc.stdout):
                try: f.close()
                except OSError: pass
        return False


def nexus_tools(config_path, provider, timeout=15):
    config = read_configuration(config_path)
    server = config["servers"].get(provider)
    if server is None:
        raise REBError("Nexus não tem esse fornecedor configurado")
    with MCPStdioClient(server["command"], timeout=timeout) as client:
        discovered = client.list_tools()
    return {"provider": provider, "available": [
        {"name": t.get("name"), "description": t.get("description", "")[:300], "permission": server.get("allowed_tools", {}).get(t.get("name"), "blocked")}
        for t in discovered if isinstance(t, dict)
    ], "note": "blocked não pode ser executada até o operador a autorizar na configuração local."}


def nexus_call(config_path, provider, tool, arguments, *, approved_external=False, approved_write=False, timeout=15):
    config = read_configuration(config_path)
    server = config["servers"].get(provider)
    if server is None:
        raise REBError("Servidor Nexus desconhecido")
    permission = server.get("allowed_tools", {}).get(tool)
    if permission not in {"read", "write"}:
        raise REBError("Ferramenta não autorizada em allowed_tools")
    if not approved_external:
        raise REBError("Operação externa exige --approve-external explícito")
    if permission == "write" and not approved_write:
        raise REBError("Operação de escrita exige --approve-write explícito")
    if not isinstance(arguments, dict):
        raise REBError("Argumentos devem ser objeto JSON")
    with MCPStdioClient(server["command"], timeout=timeout) as client:
        discovered = {t.get("name") for t in client.list_tools() if isinstance(t, dict)}
        if tool not in discovered:
            raise REBError("Ferramenta não publicada pelo servidor MCP")
        answer = client.call_tool(tool, arguments)
    return {"provider":provider, "tool":tool, "permission":permission,
            "execution_status":"completed" if not answer.get("isError") else "remote_error",
            "result":answer, "note":"Resultado fornecido por ferramenta externa; validar antes de tratar como evidência."}
