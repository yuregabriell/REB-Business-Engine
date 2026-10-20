"""REA and RES installation diagnostics, without guessing external MCP tool names."""
import json
import os
import shutil
from pathlib import Path
from .errors import REBError
from .nexus_client import nexus_tools


def inspect_rea(config_path=None, provider='rea'):
    """Live MCP handshake when a correctly installed REA command is configured."""
    if not config_path:
        return {'provider':'rea','status':'needs_configuration','next':'Configure trusted REA MCP command and allowlisted tools in Nexus config'}
    return {'provider':'rea','status':'connected_mcp','discovery':nexus_tools(config_path,provider)}


def inspect_res(skills_root=None):
    """RES is normally an agent skill, *not* an MCP server by itself."""
    root=Path(skills_root or os.getenv('REB_RES_SKILLS_DIR','')).expanduser() if (skills_root or os.getenv('REB_RES_SKILLS_DIR')) else None
    if root is None or not root.exists():
        return {'provider':'res','status':'needs_installation','note':'Install RES in your agent host and set REB_RES_SKILLS_DIR to its skill directory.'}
    paths=[root/'SKILL.md'] if root.is_dir() else []
    paths += sorted(root.glob('**/SKILL.md'))[:30] if root.is_dir() else []
    for p in paths:
        try:
            text=p.read_text(encoding='utf8')[:10_000]
        except (OSError,UnicodeError):continue
        if ('reverse engineering saas' in text.lower() or 'res' in p.parent.name.lower()):
            return {'provider':'res','status':'skill_detected','path':str(p),'note':'Skill discovered, but execution must be mediated by a compatible host agent.'}
    return {'provider':'res','status':'skill_not_found','root':str(root)}


def diagnose_integrations(config_path=None, skills_root=None):
    try:rea=inspect_rea(config_path)
    except (REBError, OSError) as exc:rea={'provider':'rea','status':'connection_failed','detail':str(exc)[:160]}
    return {'rea':rea,'res':inspect_res(skills_root),'hubspot':{'configured':bool(os.getenv('HUBSPOT_PRIVATE_APP_TOKEN')),'kind':'read_only'}}
