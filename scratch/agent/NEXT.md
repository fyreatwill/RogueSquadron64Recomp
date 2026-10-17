# Next: offline generated-RSP-PC -> retail IMEM-PC mapping (M4 key domain)

Unit (no game run, no toolchain needed): the port's generated PCs 0x112C/0x17F0 exceed the 0x1000 IMEM range, so they are
likely generated-function IDs/offsets, not IMEM PCs. From the RSP recompiler output/generator (find where the M4 hook is
emitted under tools/fixup_*) and the Factor 5 ucode image (docs/F5-UCODE-REFERENCE.md), derive the exact arithmetic mapping
generated PC -> IMEM PC. Positive control: a PC both arms are known to execute must map correctly (the retail PC set
0x0088..0x0FE8 must be reproduced as the image of port PCs). Record the table in a REVISIT doc.
Only if the mapping is exact and justified, then (separate unit) align the origin (retail 0x006AB800 vs port 0x006AB400,
phase-gated) and join. Do not normalize PCs by guess. If no exact mapping exists, close M4 as unevaluable for the
qualified route and record that.

HYPOTHESIS-ID: m4-generated-pc-imem-mapping
