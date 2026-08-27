# s2522 generated-symbol census — `0x8006D8FC`

Date: 2026-08-26
Hypothesis: `generated-symbol-renaming-sweep`
Selected interval: main overlay `0x8006D8FC–0x8006D8FC` (4 bytes)

## Discriminator

| Address | Generated symbol/body | Companion candidate | Evidence | Confidence | Result |
|---|---|---|---|---|---|
| `0x8006D8FC` | `fake_func_8006D8FC`; one instruction, `sll v0, v1, 2` | none; companion retains `fake_func_8006D8FC` | `N64Recomp/RecompiledFuncs/funcs_16.c`, `funcs.h`, and `recomp_overlays.inl`; `rogue_squadron64/symbol_files/main_overlay.txt`; repository-wide exact-address search found no named definition, caller, or m2c source | none | unchanged |

## Competing hypotheses and outcome

- `H-named-match`: rejected; no exact companion name or clear local semantic name exists.
- `H-no-match`: selected; the complete one-symbol region has no defensible mapping.
- `H-regeneration-risk`: not exercised because there was no rename to validate; no tooling repair is indicated.

This is a static, single-source result: the companion symbol database and the
generated overlay metadata independently expose the same placeholder, while
the source-wide negative search supplies no second semantic mapping. No
generated code, symbol file, or fixup was changed.
