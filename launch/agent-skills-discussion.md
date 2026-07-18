# Proposal: portable package metadata for exporting, importing, and re-syncing Agent Skills

We are experimenting with ASXP, a packaging and lifecycle profile around an unchanged Agent Skills directory.

The problem is intentionally narrower than skill authoring: when a skill crosses an agent boundary, users need to understand package integrity, requested permissions, static snapshot versus linked source, update differences, and optional origin connections. Credentials and private knowledge must remain outside the package.

The current experiment keeps `SKILL.md` unchanged and adds an optional `asxp.json` sidecar. Clients that do not support ASXP can ignore the sidecar and consume the skill normally. The reference CLI packs the directory into `.asxp`, verifies file digests and archive safety, installs without silent overwrite, and reports permission/binding escalation between releases.

We would value feedback on:

1. Whether lifecycle metadata belongs in a sidecar or a broader package manifest.
2. How to align with existing Agent Skills metadata and distribution proposals.
3. Which fields are essential for a minimal interoperable package.
4. Which two independent clients would be useful for an import/export test.

Repository: https://github.com/tro0918/asxp

This is a draft implementation and compatibility experiment, not a claim of an adopted standard.
