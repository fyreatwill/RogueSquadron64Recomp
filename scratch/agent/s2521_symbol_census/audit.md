# s2521 generated-symbol census

Region: main overlay `0x80006BFC–0x80006BFC`, the single placeholder between
the save-data and service-worker routines in
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c`.

## Hypotheses and discriminator

- `H-named-match`: the placeholder has an exact companion symbol/source match
  and can be renamed without changing generated behavior.
- `H-no-match`: the complete region has no defensible human mapping, so the
  placeholder stays.
- `H-regeneration-risk`: an apparent name exists, but the active generation or
  fixup path cannot preserve it safely.

The discriminator is the complete placeholder table joined against the
companion symbol file, companion source search, and generated body/boundary.
An exact match would select `H-named-match`; no exact match selects
`H-no-match`; a tooling-preservation failure selects `H-regeneration-risk`.

| address | generated name | generated body/boundary | companion evidence | result |
|---|---|---|---|---|
| `0x80006BFC` | `fake_func_80006BFC` | one instruction, `sw v0, 0x18(fp)`, after the epilogue of `loadOrSaveAllEepromRecords` and before `initServiceRegistry` | `main_overlay.txt` retains the fake name; source-wide companion search found no human symbol, m2c definition, or caller attribution at this address | unchanged |

The complete region therefore selects `H-no-match`. The neighboring named
save-data and service-worker routines do not provide enough evidence to name a
standalone store fragment. This is a single-source/static result; it does not
prove the fragment is dead or permanently unnameable. No generated code,
runtime, or mitigation changed, so no build was warranted.
