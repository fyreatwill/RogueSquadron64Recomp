# Generated-symbol rename audit — Session 5111

Candidate: companion `osEepromRead = 0x8002A340`.

- The companion symbol file supplies the semantic name and address; the next
  companion entry is `osEepromWrite` at `0x8002A660`.
- The generated snapshot contains no `func_8002A340` or
  `fake_func_8002A340` prologue/body. It contains only the host-wrapper
  declaration and overlay entry for `osEepromRead_recomp`.
- `recomp_overlays.inl` records `osEepromRead_recomp` at offset `0x29F00`
  with `rom_size = 0`, confirming this is an externally implemented wrapper,
  not a generated text span.
- The bounded generated-reference search found zero direct generated callers.
- The bounded companion helper selected zero generated renames and reported
  the candidate as already synchronized under its placeholder-only policy.

The host ABI name remains `osEepromRead_recomp`; changing it would require
coordinated runtime-wrapper edits, not a generated-symbol rename. This
candidate therefore selects the host-wrapper hypothesis. No build or soak was
run.
