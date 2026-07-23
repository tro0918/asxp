ASXP 0.2 now has a package schema, zero-dependency Python reference CLI, 20-case Core TCK, and an interactive demo. The next milestone is proving that one unchanged package can cross independently implemented runtimes.

We are looking for maintainers or contributors interested in one of these adapters:

- Another Agent Skills-compatible client
- LangGraph or another Python agent runtime
- MCP Skills Extension / SEP-2640 compatibility
- TypeScript reference packer and verifier

An implementation should publish:

1. Runtime and adapter version
2. Export, verify, import, and update-diff results
3. TCK result
4. Known conversion loss or unsupported bindings

Useful links:

- Specification: https://github.com/tro0918/asxp/blob/main/spec/ASXP-0.2.md
- Package schema: https://github.com/tro0918/asxp/blob/main/schemas/package.schema.json
- TCK: https://github.com/tro0918/asxp/tree/main/tck
- Interactive demo: https://tro0918.github.io/asxp/demo/

Please comment with the runtime you want to integrate before starting substantial work so we can keep adapters independent and avoid duplication.
