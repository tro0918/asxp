# ASXP 0.2.0 — package and lifecycle profile

ASXP 0.2 reframes the project as a portable packaging and lifecycle profile around an unchanged Agent Skills directory.

## Highlights

- Standard Agent Skills-compatible `SKILL.md`
- Optional `asxp.json` sidecar
- Deterministic ZIP-based `.asxp` artifacts
- `pack`, `verify`, `install`, and `diff` CLI commands
- Per-file SHA-256 integrity and package revision
- Archive traversal and credential-like filename rejection
- Permission and binding escalation detection
- Optional embedded, MCP, ASXP HTTP, and A2A bindings
- 20-case Core TCK with machine-readable result
- Interactive two-agent browser demo
- GitHub Pages, governance, security, RFC, and issue templates

This is a draft interoperability release, not an adopted standard. Feedback and independent runtime implementations are especially welcome.

## Verify the release

```bash
python3 -m unittest discover -s tests -v
python3 scripts/run_tck.py
python3 -m src.asxp.cli pack examples/v0.2/refund-policy -o refund-policy.asxp
python3 -m src.asxp.cli verify refund-policy.asxp
```
