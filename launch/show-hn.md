# Show HN: ASXP – export and import an AI agent skill without sharing credentials or private knowledge

Agent Skills makes reusable instructions portable, but moving a skill between agents raises another set of questions: what permissions does it request, where did it come from, what changed since the last import, and how can the original agent be consulted without copying its private RAG data?

ASXP is a draft package and lifecycle profile around an unchanged `SKILL.md`. It adds an optional `asxp.json`, deterministic `.asxp` archives, per-file integrity, safe installation, permission/binding diffs, and optional origin metadata.

The repo includes a zero-dependency Python CLI, schemas, conformance tests, and a browser demo with two simulated agents. It does not replace Agent Skills or MCP; MCP is one optional binding.

I am looking for criticism and, more importantly, a second independent runtime to test import/export interoperability.

https://github.com/tro0918/asxp
