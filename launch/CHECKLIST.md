# Public launch checklist

- [ ] Run `bash scripts/publish_github.sh` from the repository root.
- [ ] Push commit `d7c52ff` or its descendant to `main`.
- [ ] Confirm Conformance workflow passes.
- [ ] Enable GitHub Pages with GitHub Actions as the source if the workflow requests it.
- [ ] Confirm `https://tro0918.github.io/asxp/` and `/demo/` load.
- [ ] Create GitHub release `v0.2.0` using `release-notes-v0.2.0.md`.
- [ ] Add repository description: `Portable packaging, integrity, permissions, and lifecycle for Agent Skills.`
- [ ] Add topics: `agent-skills`, `mcp`, `ai-agents`, `interoperability`, `skill-package`, `agent-protocol`.
- [ ] Enable Discussions and private vulnerability reporting.
- [ ] Post `agent-skills-discussion.md` to the Agent Skills community.
- [ ] Run `bash scripts/publish_outreach.sh` to create the implementer issue and Agent Skills Discussion.
- [ ] Share `mcp-wg-intro.md` in the Skills Over MCP WG before proposing a SEP.
- [ ] Publish the Show HN post only after the live demo and CI are green.
- [ ] Recruit a second independent runtime and publish its TCK result.
