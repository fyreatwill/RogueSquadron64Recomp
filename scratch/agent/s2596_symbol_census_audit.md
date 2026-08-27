# s2596 static symbol census: `0x800CC3D4`

## Discriminator table

| Check | Observation | Consequence |
|---|---|---|
| Generated span | `funcs_37.c` has `calculateShotAccuracy` at `0x800CC374`, ending with `jr`/delay-slot `nop` at `0x800CC3CC–0x800CC3D0`; the next emitted body is `fake_func_800CC3D4` and contains only `__builtin_trap()` | The target is not a complete independently generated body in the current output |
| Neighboring code | The generated stream resumes at `tickAtAtAudioAndWeaponState` at `0x800CC9B8`; the missing interval is `0x800CC3D4–0x800CC9B7` | No complete function boundary or body is available to name |
| Companion symbol | `rogue_squadron64/symbol_files/menu_overlay.txt` retains `fake_func_800CC3D4 = 0x800CC3D4`; no semantic name or comment is supplied | Companion mapping hypothesis is not supported |
| Exact source/m2c search | `rg` over companion source, docs, symbol files, and generated output found no alternate name or exact-address definition; nearby named symbols are `calculateShotAccuracy` (`0x800CC374`) and `tickAtAtAudioAndWeaponState` (`0x800CC9B8`) | No independent semantic match |
| Caller search | No generated call site targets `0x800CC3D4`; the only occurrence after the preceding function is the placeholder declaration/entry and comments from the overlapping decode | No callable function identity to infer |
| Rename generator | `python3 tools/rename/build_redefs.py` completed with `RC=0`, wrote `9792` lines, and emitted no `800CC3D4` mapping | No tool/input mismatch; existing mappings remain intact |

## Verdict

`H-BoundaryOnly` is selected. Leave `fake_func_800CC3D4` unchanged. The
placeholder is a trap-only gap-filler associated with an incomplete/invalid
decode, not a defensible human-named function. This is a static, single-source
classification; it does not imply that the underlying ROM bytes are dead or
that the runtime trap is safe to execute.

