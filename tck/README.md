# ASXP Technology Compatibility Kit

The TCK defines observable behavior for ASXP 0.2 implementations. A conforming Core implementation must pass equivalent tests for:

1. Standard Agent Skills `SKILL.md` parsing.
2. Required `asxp.json` fields and SemVer validation.
3. Deterministic package revision generation.
4. Per-file SHA-256 integrity verification.
5. Archive path traversal rejection.
6. Credential-like file rejection.
7. HTTPS-only external bindings.
8. Package/skill name consistency.
9. Permission escalation detection.
10. Binding addition detection.
11. Existing installation protection unless force is explicit.
12. Unknown extension preservation.

Run the reference implementation:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/run_tck.py > tck-result.json
```

Publish `tck-result.json` with compatibility claims. Its format is defined by `result.schema.json`.
