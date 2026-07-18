---
name: policy-advisor
description: Explain policy clauses and delegate questions that require the origin agent's private policy index.
asxp-version: 0.1
version: 2.1.0
id: asxp://example.org/policy-advisor
revision: sha256:1b93example
publisher: example.org
privacy: delegated
permissions: skill.delegate.policy-advisor
origin-url: https://agents.example.org/v1/skills/policy-advisor
delegation-url: https://agents.example.org/v1/delegations
signing-key-id: example-2026-01
ae-tools-json: '[]'
---

# Policy advisor

Answer from the user's supplied text when possible. Delegate only when the answer depends on material held in the origin's private policy index. Send the minimum necessary excerpt and explain that external processing is required before calling the delegated tool.
