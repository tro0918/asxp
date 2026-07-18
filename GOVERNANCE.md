# Governance

ASXP uses open, evidence-driven governance during the draft phase.

## Principles

- Preserve Agent Skills compatibility.
- Prefer small profiles and existing protocols over duplicated mechanisms.
- Require two independent implementations before declaring a feature stable.
- Treat security and conformance tests as normative engineering work.
- Document dissent and migration costs.

## Decisions

Minor editorial changes use pull requests. Observable behavior and schema changes require an RFC under `rfcs/`, a reference implementation or executable example, security analysis, backward-compatibility analysis, and TCK coverage.

Draft consensus is reached when maintainers and affected implementers have had at least 14 days to review and no unresolved blocking interoperability objection remains. Maintainers document the rationale for acceptance or rejection.

## Roles

- Contributor: submits issues, tests, docs, adapters, or RFC feedback.
- Implementer: maintains an independent ASXP integration and publishes conformance results.
- Maintainer: reviews changes, manages releases, and applies the security process.

The project should add maintainers from independent organizations after sustained contributions. No single vendor receives permanent control over the specification.

## Compatibility claims

Projects may claim `ASXP 0.2 Core compatible` only when they publish their TCK result, implementation version, tested platform, and known deviations.
