# Contributing

ASXP prioritizes demonstrated interoperability over speculative fields.

## Before proposing a change

Describe the cross-runtime problem, affected profile, concrete package, conversion loss, security impact, and observable expected behavior. Use a regular issue for bugs and an RFC for schema or protocol behavior.

Protocol changes should include:

- an RFC based on `rfcs/0000-template.md`;
- reference implementation or executable example;
- backward-compatibility and migration analysis;
- security and privacy analysis;
- conformance test coverage.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 -m src.asxp.cli pack examples/v0.2/refund-policy -o /tmp/refund-policy.asxp
python3 -m src.asxp.cli verify /tmp/refund-policy.asxp
```

New normative requirements use RFC 2119 language. Never commit credentials or real private knowledge in fixtures. By contributing, you agree that your contribution is licensed under Apache-2.0.
