#!/usr/bin/env python3
"""Install REB Agent Skills by copying readable instruction directories.

No network access or shell calls. Existing skills are not overwritten by default.
"""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / 'skills'
TARGETS = {
    'claude': Path.home() / '.claude' / 'skills',
    'codex': Path.home() / '.codex' / 'skills',
    'cursor': Path.home() / '.cursor' / 'skills',
    'project': Path.cwd() / '.agents' / 'skills',
}

def install(target: Path, *, dry_run: bool = False, force: bool = False) -> list[dict]:
    result=[]
    if not SKILLS.is_dir(): raise SystemExit('Skills source missing')
    for source in sorted(SKILLS.iterdir()):
        if not source.is_dir() or not (source/'SKILL.md').exists(): continue
        dest = target/source.name
        if dest.exists() and not force:
            result.append({'skill':source.name,'state':'skipped_existing','target':str(dest)})
            continue
        if not dry_run:
            if dest.exists(): shutil.rmtree(dest)
            target.mkdir(parents=True,exist_ok=True)
            shutil.copytree(source,dest)
        result.append({'skill':source.name,'state':'planned' if dry_run else 'installed','target':str(dest)})
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Install REB skills for a compatible host')
    p.add_argument('--host',choices=TARGETS.keys(),default='project')
    p.add_argument('--target',type=Path)
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--force',action='store_true')
    args=p.parse_args()
    for r in install(args.target or TARGETS[args.host],dry_run=args.dry_run,force=args.force):
        print(f"{r['state']:17} {r['skill']} -> {r['target']}")
