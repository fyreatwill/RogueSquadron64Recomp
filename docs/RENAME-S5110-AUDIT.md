# Generated-symbol rename audit — Session 5110

Candidate: companion `osEepromProbe = 0x8002A2A0`.

- The companion symbol file supplies the semantic name and address.
- The generated snapshot contains no `func_8002A2A0` or
  `fake_func_8002A2A0` prologue/body. It contains only the host-wrapper
  declaration and one call to `osEepromProbe_recomp`.
- `recomp_overlays.inl` records `osEepromProbe_recomp` at offset `0x29E60`
  with `rom_size = 0`, confirming this is an externally implemented wrapper,
  not a generated text span. The following companion entry is
  `osEepromRead` at `0x8002A340`.
- One generated caller exists in `funcs_2.c`, at guest callsite `0x800063F4`.
- The bounded companion helper selected zero generated renames and reported
  the candidate as already synchronized under its placeholder-only policy.

The host ABI name remains `osEepromProbe_recomp`; changing it would require
coordinated runtime-wrapper and generated-call edits, not a generated-symbol
rename. This candidate therefore selects the host-wrapper hypothesis. No
build or soak was run.
