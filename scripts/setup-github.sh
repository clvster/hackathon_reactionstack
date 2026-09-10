#!/usr/bin/env bash
set -euo pipefail

REPO="${1:?usage: scripts/setup-github.sh owner/repo}"
DIR="$(cd "$(dirname "$0")" && pwd)"

if ! gh api "repos/$REPO/git/ref/heads/dev" >/dev/null 2>&1; then
  MAIN_SHA="$(gh api "repos/$REPO/git/ref/heads/main" -q .object.sha)"
  gh api "repos/$REPO/git/refs" -f ref=refs/heads/dev -f sha="$MAIN_SHA" >/dev/null
  echo "created branch dev"
fi

gh repo edit "$REPO" \
  --default-branch dev \
  --enable-squash-merge \
  --enable-merge-commit \
  --enable-rebase-merge=false \
  --delete-branch-on-merge
echo "repo settings updated"

for name in dev main; do
  id="$(gh api "repos/$REPO/rulesets" -q ".[] | select(.name == \"$name\") | .id")"
  if [ -n "$id" ]; then
    gh api -X PUT "repos/$REPO/rulesets/$id" --input "$DIR/rulesets/$name.json" >/dev/null
    echo "ruleset $name updated"
  else
    gh api -X POST "repos/$REPO/rulesets" --input "$DIR/rulesets/$name.json" >/dev/null
    echo "ruleset $name created"
  fi
done

for env in dev prod; do
  gh api -X PUT "repos/$REPO/environments/$env" >/dev/null
  echo "environment $env ready"
done
