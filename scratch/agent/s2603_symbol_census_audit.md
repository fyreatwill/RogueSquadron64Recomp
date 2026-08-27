# s2603 generated-symbol census

## Discriminator

The selected placeholder was `0x800E447C`, the first unresolved entry after
`0x800E406C` in the mission overlay. The competing outcomes were:

- `H-CompanionMapping`: an exact companion-defined semantic name exists.
- `H-BoundaryOnly`: the bytes are an incomplete or duplicate-symbol boundary
  fragment and should remain generated-address named.
- `H-ToolMismatch`: generated and companion inputs disagree in a way that
  requires repairing the rename path.

## Evidence

- `RecompiledFuncs/funcs_39.c` emits a four-byte function at `0x800E447C`
  containing `lhu $v0, 0x14($v1)` and `lw $a0, 0x58($fp)`.
- It is immediately after the complete `handleRayShieldedNpcDestroy` body,
  which ends at `0x800E4478`, and immediately before the complete
  `resetCraftInstanceMotionState` body at `0x800E4480`.
- `rogue_squadron64/symbol_files/mission_overlay.txt` retains
  `fake_func_800E447C` and comments that `func_800E4480` was deleted because
  of a duplicate-symbol collision with `resetCraftInstanceMotionState`.
- Exact-address searches across companion source, m2c, callers, and alternate
  symbol names found no semantic candidate for `0x800E447C`.
- `python3 tools/rename/build_redefs.py` completed successfully and emitted no
  mapping for `fake_func_800E447C`.

## Result

`H-BoundaryOnly` selected. No mapping was added; the placeholder remains
unchanged. The next sweep address is `0x800E71C8`.
