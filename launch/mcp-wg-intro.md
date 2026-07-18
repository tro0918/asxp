# ASXP introduction for Skills Over MCP WG

We are implementing a small package/lifecycle layer around Agent Skills: export, integrity, permission review, installation, update diff, Re-sync metadata, and optional origin bindings.

We do not want to duplicate the MCP Skills Extension. The ASXP 0.2 draft leaves `SKILL.md` unchanged and can reference MCP as a runtime binding. Our main question is whether installable package lifecycle—especially offline export/import, integrity, permission escalation, and source synchronization—can be a complementary experiment to the WG's skill discovery and consumption work.

Specific feedback requested:

- How should `asxp.json` relate to the Registry WG `skills.json` proposal?
- Can an MCP Resources-based skill be exported into an offline ASXP package without losing identity?
- Which permission/binding changes should require client re-approval?
- Would a compatibility adapter against SEP-2640 be useful as an experimental result?

Repository and runnable demo: https://github.com/tro0918/asxp
