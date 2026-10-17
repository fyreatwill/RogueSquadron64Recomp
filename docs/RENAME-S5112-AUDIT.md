# Generated-symbol rename audit — Session 5112

Candidate: companion `osEepromWrite = 0x8002A660`.

- The companion symbol file supplies the semantic name and address; the next
  companion entry is `osContStartQuery` at `0x8002AB80`.
- The generated snapshot contains no `func_8002A660` or
  `fake_func_8002A660` prologue/body. It contains only the host-wrapper
  declaration and overlay entry for `osEepromWrite_recomp`.
- `recomp_overlays.inl` records `osEepromWrite_recomp` with `rom_size = 0`,
  confirming this is an externally implemented wrapper, not a generated text
  span.
- The bounded generated-reference search found zero direct generated callers.
- The bounded companion helper selected zero generated renames and reported
  the candidate as already synchronized under its placeholder-only policy.

The host ABI name remains `osEepromWrite_recomp`; changing it would require
coordinated runtime-wrapper edits, not a generated-symbol rename. This
candidate therefore selects the host-wrapper hypothesis. No build or soak was
run.
