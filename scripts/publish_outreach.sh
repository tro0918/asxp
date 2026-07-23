#!/usr/bin/env bash
set -euo pipefail

project_repo="tro0918/asxp"
upstream_repo="agentskills/agentskills"
discussion_title="Proposal: portable package metadata for exporting, importing, and re-syncing Agent Skills"
issue_title="Independent runtime implementers wanted for ASXP 0.2"

if ! command -v gh >/dev/null 2>&1; then
  echo "error: GitHub CLI (gh) is required" >&2
  exit 1
fi

gh auth status -h github.com

existing_issue="$(
  gh issue list \
    --repo "$project_repo" \
    --state all \
    --search "\"$issue_title\" in:title" \
    --json title,url \
    --jq ".[] | select(.title == \"$issue_title\") | .url" |
    head -n 1
)"

if [[ -n "$existing_issue" ]]; then
  echo "implementer issue already exists: $existing_issue"
else
  issue_url="$(
    gh issue create \
      --repo "$project_repo" \
      --title "$issue_title" \
      --body-file launch/implementers-issue.md
  )"
  echo "created implementer issue: $issue_url"
fi

repo_id="$(
  gh api graphql \
    -f query='query { repository(owner:"agentskills", name:"agentskills") { id } }' \
    --jq '.data.repository.id'
)"

category_id="$(
  gh api graphql \
    -f query='query { repository(owner:"agentskills", name:"agentskills") { discussionCategories(first:50) { nodes { id name } } } }' \
    --jq '.data.repository.discussionCategories.nodes[] | select((.name | ascii_downcase) == "ideas") | .id' |
    head -n 1
)"

if [[ -z "$category_id" ]]; then
  category_id="$(
    gh api graphql \
      -f query='query { repository(owner:"agentskills", name:"agentskills") { discussionCategories(first:50) { nodes { id name } } } }' \
      --jq '.data.repository.discussionCategories.nodes[] | select((.name | ascii_downcase) == "general") | .id' |
      head -n 1
  )"
fi

if [[ -z "$category_id" ]]; then
  echo "error: no Ideas or General discussion category is available in $upstream_repo" >&2
  exit 1
fi

existing_discussion="$(
  gh api graphql \
    -f query='query { repository(owner:"agentskills", name:"agentskills") { discussions(first:100) { nodes { title url } } } }' \
    --jq ".data.repository.discussions.nodes[] | select(.title == \"$discussion_title\") | .url" |
    head -n 1
)"

if [[ -n "$existing_discussion" ]]; then
  echo "Agent Skills discussion already exists: $existing_discussion"
else
  discussion_url="$(
    gh api graphql \
      -f query='mutation($repo:ID!, $category:ID!, $title:String!, $body:String!) { addDiscussion(input:{repositoryId:$repo, categoryId:$category, title:$title, body:$body}) { discussion { url } } }' \
      -f repo="$repo_id" \
      -f category="$category_id" \
      -f title="$discussion_title" \
      -F body=@launch/agent-skills-discussion.md \
      --jq '.data.addDiscussion.discussion.url'
  )"
  echo "created Agent Skills discussion: $discussion_url"
fi

echo
echo "Manual community posts remain:"
echo "1. MCP Skills Over MCP WG Discord (#skills-over-mcp-wg)"
echo "   Copy: launch/mcp-wg-intro.md"
echo "2. Show HN, after upstream feedback"
echo "   Copy: launch/show-hn.md"
