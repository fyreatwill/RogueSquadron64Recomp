# Generated-symbol rename audit — Session 5109

Candidate: companion `osEepromLongWrite = 0x8002A1B0`.

- The companion symbol file supplies the semantic name and address.
- The generated snapshot contains no `func_8002A1B0` or
  `fake_func_8002A1B0` prologue/body. It contains only the host-wrapper
  declaration and calls to `osEepromLongWrite_recomp`.
- `recomp_overlays.inl` records `osEepromLongWrite_recomp` at offset
  `0x29D70` with `rom_size = 0`, confirming this is an externally implemented
  wrapper rather than a generated text span. The following companion entry is
  `osEepromProbe` at `0x8002A2A0`.
- Three generated callers exist in `funcs_2.c`, at guest callsites
  `0x80006524`, `0x800069EC`, and `0x80006B70`.
- The bounded companion helper selected no generated rename and reported the
  candidate as already synchronized under its placeholder-only policy.

The host ABI name remains `osEepromLongWrite_recomp`; changing it would require
coordinated runtime-wrapper and generated-call edits, not a generated-symbol
rename. This candidate therefore selects the host-wrapper hypothesis. No
build or soak was run.
