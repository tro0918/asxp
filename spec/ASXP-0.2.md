# ASXP 0.2 — Agent Skill Package and Lifecycle Profile

Status: Draft. The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are interpreted as RFC 2119/8174 requirements.

## 1. Scope

ASXP 0.2 defines an installable package around an unchanged Agent Skills directory. It standardizes package metadata, content integrity, permissions, runtime binding declarations, installation, update comparison, and optional source synchronization. It does not standardize model APIs, inference, RAG internals, billing, or a universal agent task protocol.

## 2. Artifact

The file extension is `.asxp`. The media type is `application/vnd.asxp.package+zip;version=0.2`. The artifact is a ZIP archive with `SKILL.md` and `asxp.json` at its root. It MAY contain `scripts/`, `references/`, `assets/`, and other files permitted by Agent Skills.

Readers MUST reject absolute archive paths, `..` traversal, duplicate critical entries, archives over their configured limits, and decompression bombs. The reference limits are 10 MiB and 256 files.

## 3. Agent Skills compatibility

`SKILL.md` MUST conform to the Agent Skills format and MUST NOT require ASXP-specific fields. An implementation that does not support ASXP can ignore `asxp.json` and consume the skill normally.

## 4. Sidecar manifest

`asxp.json` MUST conform to `schemas/package.schema.json`.

Required fields:

- `specVersion`: `0.2`
- `package.name`: equal to the `SKILL.md` name
- `package.version`: SemVer
- `skill.entrypoint`: `SKILL.md`
- `permissions`: unique requested permission identifiers
- `bindings`: zero or more runtime bindings

Optional fields include publisher, license, skill ID, privacy, origin, integrity, and extensions.

## 5. Bindings

Bindings describe optional runtime connections. They do not carry credentials.

- `embedded`: JSON Schema tool contracts included in the package.
- `mcp`: an MCP server identity and optional tool allowlist.
- `asxp-http`: the minimal synchronous origin-delegation endpoint.
- `a2a`: an A2A Agent Card and remote skill ID.

Importers MAY support any subset. A common binding is negotiated; otherwise the skill remains usable inline without remote delegation.

## 6. Integrity and revision

Packers compute SHA-256 for every packaged file except `asxp.json` and store the map under `integrity.files`. The manifest revision is SHA-256 over canonical JSON after integrity has been added and before `revision` is added. Canonical JSON sorts object keys, uses UTF-8, and has no insignificant whitespace.

Verifiers MUST validate every listed file digest, reject unlisted critical files according to policy, recompute the revision, and ensure `SKILL.md` name equals `package.name`. A future signature profile may bind publisher identity to the revision; unsigned packages remain valid but MUST be surfaced as unsigned.

## 7. Export

Exporters MUST exclude credentials, channel tokens, conversation history, raw private knowledge bases, embeddings, private indexes, and hidden host policies. Exporters SHOULD detect credential-like filenames and content. Exporters MUST generate a fresh integrity map and revision.

## 8. Import and activation

Installation and activation are separate operations.

1. Verify archive safety, manifest, integrity, and revision.
2. Display publisher, unsigned/signed state, permissions, privacy, origin, and bindings.
3. Apply host allow/deny policy.
4. Install into a non-active staging location.
5. Activate only after required approval.

An importer MUST NOT silently overwrite an existing installation. Tool name collisions MUST be deterministic and MUST NOT replace existing host tools silently.

## 9. Update and Re-sync

A static package has no `origin`. A linked package contains `origin.syncUrl` and an immutable installed revision. Re-sync SHOULD use HTTP conditional requests with the installed revision as ETag.

Importers MUST compare permissions, bindings, privacy, origin, publisher, and instructions. Added permissions or bindings require approval. Local edits SHOULD be represented separately and re-applied with conflict reporting.

## 10. Optional origin delegation

Origin delegation is not part of Core conformance. For `asxp-http`, a host sends a task, skill ID, revision, trace ID, idempotency key, maximum depth, visited set, and declared data classes to the HTTPS endpoint. Tokens and consent artifacts are acquired out of band and never stored in the package.

Implementations MUST enforce cycle detection, depth, time, size, cost, authorization, and data-minimization policy. The recommended maximum delegation depth is 3.

## 11. Security

Implementations MUST address prompt injection, confused-deputy access, SSRF, archive traversal, decompression bombs, signature/digest confusion, replay, dependency substitution, permission escalation, and delegation cycles. Imported instructions remain below host policy. Credentials remain outside model-visible context.

## 12. Conformance

Core conformance requires standard Agent Skills parsing, sidecar validation, deterministic packing, integrity verification, safe extraction, name matching, installation protection, permission/binding diff, and unknown-extension preservation. See `tck/README.md` and reference tests.

## 13. Evolution

Minor versions may add optional fields. Major versions may change semantics. Readers reject unsupported major versions and SHOULD preserve unknown optional extensions. Changes require an RFC, security analysis, reference behavior, and conformance tests.
