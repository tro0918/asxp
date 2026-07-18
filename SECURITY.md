# Security Policy

## Reporting a vulnerability

Do not open a public issue for an unpatched vulnerability. Use GitHub private vulnerability reporting when enabled for the repository. Include affected version, attack prerequisites, minimal reproduction, impact, and suggested mitigation. Maintainers should acknowledge reports within 5 business days and coordinate disclosure after a fix is available.

## Trust model

ASXP packages are untrusted input, even when signed. A signature proves integrity and key possession, not safety. Installation is not activation. Importers must surface permissions, privacy, publisher, integrity state, origin, and runtime bindings before activation.

## Forbidden package content

Packages must not contain API keys, OAuth tokens, cookies, passwords, private certificates, channel credentials, conversation history, raw private RAG files, embeddings, private indexes, or hidden host policies.

## Required implementation defenses

- Reject archive traversal, absolute paths, duplicate critical entries, oversized packages, and decompression bombs.
- Validate manifest, tool inputs, and tool outputs.
- Require HTTPS for external origin bindings.
- Block loopback, link-local, and private destinations unless host policy explicitly allows them.
- Keep credentials outside package content and model-visible context.
- Require approval for permission, binding, publisher, or privacy escalation.
- Enforce idempotency, depth, cycle, timeout, size, rate, and cost limits for delegation.
- Minimize and redact delegated data.
- Record traceable import, activation, update, tool-call, delegation, and policy events.

## Supported versions

Draft 0.2 receives security fixes. Draft 0.1 is retained for historical compatibility and should not be used for new production deployments.
