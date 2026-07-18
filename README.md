# ASXP — Agent Skill Exchange Profile

[![Conformance](https://github.com/tro0918/asxp/actions/workflows/conformance.yml/badge.svg)](https://github.com/tro0918/asxp/actions/workflows/conformance.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Spec](https://img.shields.io/badge/spec-draft%200.2-orange.svg)](spec/ASXP-0.2.md)

**Export once. Import safely. Re-sync when the source changes. Delegate only when private knowledge is required.**

ASXP is a portable packaging and lifecycle profile for [Agent Skills](https://agentskills.io). It adds installable artifacts, integrity, permissions, origin synchronization, and optional runtime bindings without changing the standard `SKILL.md` format.

ASXP is an implementable open proposal, not an adopted standards-body specification.

## Why ASXP?

Agent Skills defines how reusable instructions and resources are authored. ASXP addresses what happens when a skill crosses an agent boundary:

- What exactly is exported?
- Which permissions and external connections are requested?
- How is package integrity checked?
- Can a static import be distinguished from a linked source?
- What changed during Re-sync, and does it need approval?
- How can the origin be consulted without copying private RAG data?

## Relationship to existing standards

| Layer | Responsibility |
|---|---|
| Agent Skills | Skill content: `SKILL.md`, scripts, references, assets |
| MCP | Optional tool and skill-distribution binding |
| A2A | Optional long-running remote-agent binding |
| **ASXP** | Installable package, integrity, permissions, provenance, import, diff, Re-sync |

ASXP does not replace Agent Skills, MCP, or A2A. A package may use `embedded`, `mcp`, `asxp-http`, or `a2a` bindings. Static packages require none of them.

## Package format

An `.asxp` artifact is a ZIP file containing an unchanged Agent Skills directory plus `asxp.json`:

```text
refund-policy.asxp
├── SKILL.md
├── asxp.json
├── scripts/       # optional
├── references/    # optional
└── assets/        # optional
```

`SKILL.md` remains valid for clients that know nothing about ASXP. `asxp.json` carries package-level information:

```json
{
  "specVersion": "0.2",
  "package": {"name": "refund-policy", "version": "1.0.0"},
  "skill": {"entrypoint": "SKILL.md"},
  "permissions": ["orders.read"],
  "privacy": "local",
  "bindings": [
    {"type": "mcp", "server": "io.example.orders", "tools": ["lookup_order"]}
  ]
}
```

## Five-minute quick start

Requires Python 3.10+ and no third-party runtime dependency.

```bash
git clone https://github.com/tro0918/asxp.git
cd asxp

# Build an installable package.
python3 -m src.asxp.cli pack examples/v0.2/refund-policy \
  --output refund-policy.asxp

# Verify manifest, revision, archive safety, and per-file integrity.
python3 -m src.asxp.cli verify refund-policy.asxp

# Install into an Agent Skills-compatible directory.
python3 -m src.asxp.cli install refund-policy.asxp \
  --target ./installed-skills
```

Compare two releases before approving an update:

```bash
python3 -m src.asxp.cli diff old.asxp new.asxp
```

`requiresApproval` becomes `true` when permissions or runtime bindings are added.

## Interactive demo

Open [`demo/index.html`](demo/index.html), or use the GitHub Pages deployment after it is enabled. The deterministic local demo shows:

1. Agent B failing before import.
2. Agent A exporting `refund-policy`.
3. Agent B importing and activating the package.
4. Tools being flattened into the host runtime.
5. Optional origin delegation for private policy knowledge.
6. Revision-aware Re-sync.

No model API key is required.

## Security boundary

ASXP packages MUST NOT contain API keys, OAuth tokens, cookies, certificates, channel credentials, conversation history, raw private knowledge bases, embeddings, or private indexes.

Importers treat every package as untrusted. Activation is separate from installation. Permission or binding increases require explicit policy approval. See [SECURITY.md](SECURITY.md).

## Repository map

- [`spec/ASXP-0.2.md`](spec/ASXP-0.2.md) — current package/lifecycle profile
- [`spec/ASXP.md`](spec/ASXP.md) — legacy 0.1 draft
- [`schemas/package.schema.json`](schemas/package.schema.json) — v0.2 sidecar schema
- [`schemas/tool.schema.json`](schemas/tool.schema.json) — embedded-tool schema
- [`src/asxp`](src/asxp) — zero-dependency reference CLI
- [`tests`](tests) and [`tck`](tck) — conformance behavior
- [`examples/v0.2`](examples/v0.2) — current examples
- [`demo`](demo) — interactive two-agent demo
- [`docs/explainer.html`](docs/explainer.html) — Korean explainer
- [`ROADMAP.md`](ROADMAP.md) — planned milestones

## Status and compatibility

- Draft 0.2 is the active design.
- Draft 0.1 remains available for comparison and migration work.
- Unknown `extensions` data should be preserved.
- Unsupported clients can ignore `asxp.json` and consume `SKILL.md` normally.

## Contributing

Interoperability evidence is more valuable than additional fields. Open a discussion or RFC with a concrete cross-runtime use case, sample package, security impact, and conformance test. See [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md).

## License

Code and specification text are available under Apache-2.0 unless a file states otherwise.
