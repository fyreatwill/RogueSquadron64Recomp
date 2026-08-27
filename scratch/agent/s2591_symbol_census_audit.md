# s2591 generated-symbol census: `0x800C5898`

## Discriminator

The competing hypotheses were `H-CompanionMapping` (an exact companion or
independent semantic name exists), `H-BoundaryOnly` (the placeholder is an
incomplete fragment with no defensible name), and `H-ToolMismatch` (the rename
inputs disagree with generated coverage). The complete static table below
selects `H-BoundaryOnly`.

| Item | Observation | Outcome |
|---|---|---|
| Generated span | `RecompiledFuncs/funcs_34.c` emits `fake_func_800C5898` for `0x800C5898` and `0x800C589C`, two instructions / 8 bytes: `lui $at,0x801A`; `addu $at,$at,$a0` | bounded fragment |
| Preceding body | The preceding generated body reaches `0x800C5894` (`jal 0x8001C5F4`) and has the `0x800C5898` instruction as its delay-slot overlap in the preceding control-flow rendering | entry/delay-slot boundary |
| Following body | `menuOverlayInit` starts at `0x800C58A0`; the fragment ends immediately before it | not a complete callable body |
| Companion input | `symbol_files/menu_overlay.txt` retains only `fake_func_800C5898 = 0x800C5898` with no semantic comment or alias | no direct mapping |
| Source/m2c evidence | `docs/mips_to_c/ctx.c` has only `void func_800C5898(struct D_80130B40_type *arg0, s32 arg1, s32 arg2);`; no body or human name is supplied | no independent semantic match |
| Caller/alias evidence | Exact-address search found no caller or alternate symbol beyond the generated placeholder and the unimplemented context declaration | no defensible inferred name |
| Generator coverage | `python3 tools/rename/build_redefs.py` completed successfully, wrote 9,792 redef lines, and emitted no `800C5898` mapping; existing `menuOverlayInit` mappings remained present | rejects tool mismatch |

No mapping is justified. The placeholder remains unchanged. This is a static
single-source boundary classification; no runtime behavior was tested.
