#!/usr/bin/env bash
# Publish this repository using the operator's GitHub CLI authentication.
# Handles both an already-created empty repository and a repo not yet created.
set -euo pipefail
OWNER="${1:?Usage: scripts/publish-github.sh OWNER [private|public]}"
VISIBILITY="${2:-private}"
if [[ "$VISIBILITY" != "private" && "$VISIBILITY" != "public" ]]; then
  echo "visibility must be private or public" >&2; exit 2
fi
command -v gh >/dev/null || { echo 'Install GitHub CLI (gh) and run gh auth login first.' >&2; exit 2; }
command -v git >/dev/null || { echo 'Install git first.' >&2; exit 2; }
gh auth status >/dev/null || { echo 'Login to GitHub first: gh auth login' >&2; exit 2; }
cd "$(dirname "$0")/.."
if [[ ! -d .git ]]; then git init -b main; fi
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  git add .
  git commit -m 'feat: initialize REB business engine'
fi
REPO_NAME="${REB_REPOSITORY_NAME:-REB-Business-Engine}"
REPO="$OWNER/$REPO_NAME"
if gh repo view "$REPO" >/dev/null 2>&1; then
  echo "Repository $REPO exists; pushing local main."
  if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "https://github.com/$REPO.git"
  fi
  git push -u origin main
else
  echo "Creating $REPO with $VISIBILITY visibility."
  gh repo create "$REPO" "--$VISIBILITY" --source . --remote origin --push
fi
