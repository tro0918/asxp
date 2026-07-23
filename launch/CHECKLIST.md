# Public launch checklist

- [x] Run `bash scripts/publish_github.sh` from the repository root.
- [x] Push commit `d7c52ff` or its descendant to `main`.
- [x] Confirm Conformance workflow passes.
- [x] Enable GitHub Pages with GitHub Actions as the source if the workflow requests it.
- [x] Confirm `https://tro0918.github.io/asxp/` and `/demo/` load.
- [x] Create GitHub release `v0.2.0` using `release-notes-v0.2.0.md`.
- [x] Add repository description: `Portable packaging, integrity, permissions, and lifecycle for Agent Skills.`
- [x] Add topics: `agent-skills`, `mcp`, `ai-agents`, `interoperability`, `skill-package`, `agent-protocol`.
- [x] Enable Discussions and private vulnerability reporting.
- [ ] Post `agent-skills-discussion.md` to the Agent Skills community.
- [x] Create the [independent implementers issue](https://github.com/tro0918/asxp/issues/2).
- [ ] Share `mcp-wg-intro.md` in the Skills Over MCP WG before proposing a SEP.
- [ ] Publish the Show HN post only after the live demo and CI are green.
- [ ] Recruit a second independent runtime and publish its TCK result.
