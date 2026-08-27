# s2600 generated-symbol census

- Address/span: `0x800DD2C4–0x800DD2CF` (12 bytes), in `funcs_38.c`.
- Generated instructions: `nop`; `lw $v0, 0x74($fp)`; `sw $zero, 0x34($v0)`.
- Neighboring body: `npcInitFullModel` starts at `0x800DD2D0` and is complete.
- Companion evidence: `mission_overlay.txt` defines
  `duplicateSymbolPrefixForNpcInitFullModel = 0x800DD2C4` and documents the
  following duplicate `func_800DD2D0` deletion.
- Decision: `H-CompanionMapping`; add the exact mapping to `build_redefs.py`.
- No runtime build or game run was needed for this static rename unit.
