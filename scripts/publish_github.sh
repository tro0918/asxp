#!/usr/bin/env bash
set -euo pipefail

repo="tro0918/asxp"
release="v0.2.0"

if ! command -v gh >/dev/null 2>&1; then
  echo "error: GitHub CLI (gh) is required" >&2
  exit 1
fi

gh auth status -h github.com

python3 -m unittest discover -s tests -v
python3 scripts/run_tck.py
python3 -m src.asxp.cli pack examples/v0.2/refund-policy -o /tmp/refund-policy.asxp
python3 -m src.asxp.cli verify /tmp/refund-policy.asxp

git diff --check
if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: working tree is not clean" >&2
  exit 1
fi

git push origin main

if gh release view "$release" --repo "$repo" >/dev/null 2>&1; then
  echo "release $release already exists"
else
  gh release create "$release" \
    --repo "$repo" \
    --target main \
    --title "ASXP 0.2.0 — Package and Lifecycle Profile" \
    --notes-file launch/release-notes-v0.2.0.md
fi

gh repo edit "$repo" \
  --description "Portable packaging, integrity, permissions, and lifecycle for Agent Skills." \
  --enable-discussions=true \
  --add-topic agent-skills \
  --add-topic mcp \
  --add-topic ai-agents \
  --add-topic interoperability \
  --add-topic skill-package \
  --add-topic agent-protocol

echo
echo "Repository: https://github.com/$repo"
echo "Release:    https://github.com/$repo/releases/tag/$release"
echo "Pages:      https://tro0918.github.io/asxp/"
echo
echo "Recent workflow runs:"
gh run list --repo "$repo" --limit 5
