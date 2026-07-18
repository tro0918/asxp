# Agent Skill Exchange Protocol (ASXP)

ASXP is a vendor-neutral, file-first protocol for exporting, importing, syncing, and optionally delegating agent skills. It keeps the familiar `SKILL.md` shape while making tools, provenance, permissions, and remote delegation machine-readable.

Status: **Draft 0.1.0**. This repository is an implementable proposal, not an adopted standards-body specification.

## Design goals

- A skill remains readable Markdown with YAML frontmatter.
- An imported skill can run inline using its prompt and tool contracts.
- Remote delegation is optional and never required for static snapshots.
- Knowledge files, secrets, tokens, and channel credentials are excluded.
- Implementations can validate the portable core without understanding vendor extensions.
- Tools use standard JSON Schema contracts; remote operations use HTTP/OpenAPI.

## Quick start

```bash
python3 -m src.asxp.cli validate examples/customer-support.skill.md
python3 -m src.asxp.cli inspect examples/customer-support.skill.md
python3 -m unittest discover -s tests -v
```

No third-party runtime dependency is required for the reference CLI.

## Repository layout

- `spec/ASXP.md` — normative protocol specification
- `spec/ASXP-KO.md` — Korean implementation specification with wire examples and state model
- `spec/openapi.yaml` — registry, resolution, sync, and delegation API
- `schemas/` — JSON Schemas for manifests and tools
- `examples/` — portable and linked skill examples
- `src/asxp/` — parser, validator, and CLI
- `tests/` — conformance-oriented tests
- `demo/` — interactive two-agent export/import/delegation demo
- `docs/explainer.html` — standalone Korean protocol explainer

## Interactive demo

Open `demo/index.html` in a browser. The demo lets you compare Agent B before and after importing Agent A's skill, inspect flattened tools, trigger optional origin delegation, and observe Re-sync events. It is a deterministic local simulation and does not require an API key.

## Skill lifecycle

```text
Agent A --export--> skill.md --import--> Agent B
   |                                  |  inline prompt + tools
   +---- optional signed origin ------+-- delegate only when needed
                         Registry <--- resolve / sync / revoke
```

## Compatibility

ASXP accepts `SKILL.md` with scalar YAML fields and defines `ae-tools-json` as a compact compatibility field. The canonical wire representation is the JSON manifest in `schemas/skill-manifest.schema.json`. Implementations should preserve unknown `x-*` extensions.

## Security promise

Exporters MUST NOT embed credentials, raw knowledge files, conversation history, or channel tokens. Importers MUST treat instructions and tools as untrusted, show requested permissions, and require policy approval before activation. See the security section in the specification.

## License

Apache-2.0. See `LICENSE`.
