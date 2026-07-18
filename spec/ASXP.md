# Agent Skill Exchange Protocol 0.1

## 1. Status and terminology

This document is a vendor-neutral draft. The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, and MAY are to be interpreted as described by RFC 2119 and RFC 8174.

An **exporter** creates a skill package. An **importer** installs it. An **origin** is an agent runtime able to serve updates or delegated requests. A **registry** resolves stable skill identifiers to immutable releases. A **snapshot** has no live origin relationship. A **linked skill** retains an origin relationship and can be re-synced.

## 2. Conformance profiles

| Profile | Required behavior |
|---|---|
| Core | Parse/export `skill.md`, validate manifest and tools, inline prompt body |
| Linked | Core + origin metadata, immutable revisions, re-sync |
| Delegating | Linked + delegated task endpoint and scoped authorization |
| Registry | Publish, resolve, fetch, revoke, key discovery |

An implementation MUST state its supported profiles. Delegation is not required for Core compatibility.

## 3. Portable skill document

The media type is `application/vnd.asxp.skill+markdown;version=0.1`. UTF-8 is REQUIRED. The document consists of YAML frontmatter followed by Markdown instructions.

Required frontmatter scalar fields:

```yaml
---
name: customer-support
description: Answer product support questions and prepare support actions.
asxp-version: 0.1
version: 1.2.0
ae-tools-json: '[{"name":"lookup_order","description":"Look up an order","inputSchema":{"type":"object","properties":{"order_id":{"type":"string"}},"required":["order_id"]}}]'
---
```

`name` MUST match `[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?`. `description` MUST explain capability and activation context. `version` SHOULD be SemVer. `ae-tools-json` MUST be a single-line JSON array and MUST conform to `tool.schema.json` item-by-item.

Optional portable scalar fields:

| Field | Meaning |
|---|---|
| `id` | Stable URI, preferably `asxp://<publisher>/<name>` |
| `revision` | Immutable origin revision or content digest |
| `publisher` | Publisher identifier or URI |
| `license` | SPDX license expression |
| `homepage` | Human-facing HTTPS URL |
| `permissions` | Space-separated permission identifiers |
| `privacy` | `local`, `delegated`, or `external` |
| `delegation-url` | HTTPS delegated task endpoint |
| `origin-url` | HTTPS metadata endpoint used for re-sync |
| `signing-key-id` | JWK `kid` expected for detached signature |
| `extensions-json` | Single-line JSON object for namespaced extensions |

The Markdown body is the inline instruction payload. Importers MUST preserve it byte-for-byte unless the user explicitly edits the installed copy. The body MUST NOT be interpreted as authority to bypass host policy.

### Canonical manifest

For signing and registry exchange, frontmatter and body are converted to the JSON form defined by `skill-manifest.schema.json`. Canonical bytes MUST use RFC 8785 JSON Canonicalization Scheme. The body is stored as `instructions`. Tools are parsed from `ae-tools-json` into `tools`.

Unknown frontmatter fields MUST be preserved on round trip. Portable extensions SHOULD use `x-<dns-name>-<field>` or be placed in `extensions-json`.

## 4. Export and import

### Export

An exporter MUST include the agent's reusable instructions and public tool contracts. It MUST NOT include:

- API keys, OAuth tokens, cookies, certificates, channel credentials, or secret environment values;
- raw knowledge/RAG files, embeddings, private indexes, or conversation history;
- hidden platform policy or unrelated system prompts;
- tool implementation secrets or internal network locations not intended for recipients.

The exporter SHOULD run secret detection and MUST declare requested permissions. Export is a snapshot unless origin metadata is explicitly attached.

### Import

An importer MUST validate syntax and tool schemas before activation. It MUST show provenance, requested permissions, tool endpoints, and whether delegation sends data externally. The importer MUST apply local allow/deny policy and SHOULD default new external tools to disabled until approved.

Tool names are flattened into the parent runtime. Collisions MUST be deterministic: the importer SHOULD namespace as `<skill-name>__<tool-name>` and MUST NOT silently replace an existing tool.

## 5. Inline execution

For each enabled skill, the importer appends the Markdown body beneath its available-skills section or an equivalent isolated instruction region. It then exposes enabled skill tools to the model using the host's native tool representation.

Hosts MUST maintain instruction precedence: host policy > user instruction > imported skill instruction. A skill cannot grant itself permissions.

Each tool call SHOULD carry an idempotency key. Hosts MUST enforce recursion depth and cycle detection across agent delegation. Recommended defaults are depth 3 and a visited tuple of `(skill id, revision, operation)`.

## 6. Origin link and re-sync

A sibling-agent import records `id`, `origin-url`, and `revision`. A file/text import without these fields is a static snapshot.

Re-sync uses conditional resolution with the installed revision. The registry/origin returns either `304 Not Modified` or a new immutable manifest plus digest and signature. Importers MUST present material permission increases for approval and MUST NOT silently activate newly added external tools. Local overrides SHOULD be represented as a patch and re-applied with conflict reporting.

## 7. Delegation

When a live origin is available, a Delegating implementation MAY synthesize one local tool named `ask_<safe-name>`. This tool maps to `POST /v1/delegations` rather than becoming part of the exported tool list.

The request includes task input, optional artifacts by reference, an execution trace identifier, maximum depth, and declared data classes. The response is either a result or an asynchronous operation. Raw origin knowledge remains at the origin.

Delegation MUST use explicit audience-bound authorization (OAuth 2.1 authorization code/client credentials as appropriate), narrow scopes such as `skill:delegate:<id>`, TLS, timeouts, and size limits. User consent MUST be obtained when policy or data classification requires it. Consent tokens MUST be audience-, purpose-, and expiry-bound and MUST NOT be persisted in `skill.md`.

## 8. Registry protocol

The normative HTTP surface is in `openapi.yaml`:

- publish an immutable release;
- resolve/fetch a release and signature;
- revoke a compromised release;
- create/poll delegated operations;
- distribute public signing keys through JWKS.

Registries MUST make releases immutable. A mutable tag such as `latest` may resolve to a revision but MUST return the immutable revision and SHA-256 digest. Revocation metadata MUST remain queryable.

## 9. Integrity and provenance

Registry envelopes use a detached JWS over RFC 8785 canonical manifest bytes. Algorithms MUST be from an explicit allowlist; `alg=none` is forbidden. Initial interoperable algorithms are EdDSA (Ed25519) and ES256. Keys are discovered through HTTPS JWKS and selected by `kid`.

Importers MUST verify the digest and signature for signed releases, bind publisher identity to an allowlisted trust policy, and surface unsigned status. A valid signature proves key possession and integrity, not safety.

## 10. Privacy and security

Implementations MUST defend against prompt injection, confused-deputy access, schema smuggling, SSRF, replay, delegation cycles, oversized payloads, and dependency substitution. At minimum:

- validate URLs and block local/link-local destinations unless host policy permits them;
- cap document, instruction, schema, request, and response sizes;
- validate tool inputs and outputs against declared schemas;
- redact secrets from logs and delegated payloads;
- isolate tool credentials from model-visible context;
- log activation, tool calls, sync, delegation, and policy decisions with trace IDs;
- allow immediate skill disablement and release revocation.

Data minimization is REQUIRED. Importers SHOULD send only task-specific excerpts during delegation, not the full conversation.

## 11. Compatibility mapping

| ASXP | Anthropic-style SKILL.md | OpenAI plugin manifest | OpenAPI |
|---|---|---|---|
| `name` | `name` | `name_for_model` | `info.title` (lossy) |
| `description` | `description` | `description_for_model` | `info.description` |
| `instructions` | Markdown body | no direct equivalent | no direct equivalent |
| `tools[]` | `ae-tools-json` extension | API operations via `api.url` | `operationId` + schemas |
| `origin.url` | `origin-url` extension | `api.url` (different semantics) | server URL |
| `permissions[]` | `permissions` extension | `auth` (partial) | security schemes (partial) |
| signature/provenance | extension | no portable equivalent | no portable equivalent |

Mappings MUST report loss. In particular, converting to a plugin manifest cannot preserve inline instructions, sync semantics, or delegation semantics without extensions.

## 12. Versioning and evolution

`asxp-version` identifies the protocol version; `version` identifies the skill release. Minor protocol versions may add optional fields. Major versions may change semantics. Readers MUST reject unsupported major versions and preserve unknown optional fields.
