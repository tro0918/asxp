# Contributing

ASXP uses specification-first changes. Open an issue describing the interoperability problem, affected conformance profiles, security impact, and a concrete example. Protocol changes should include schema changes and conformance tests.

Run before submitting:

```bash
python3 -m unittest discover -s tests -v
python3 -m src.asxp.cli validate examples/customer-support.skill.md
```

New normative requirements must use RFC 2119 language. Backward-incompatible changes require a new major protocol version. By contributing, you agree that your contribution is licensed under Apache-2.0.
