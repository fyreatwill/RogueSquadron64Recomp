# Generated-symbol rename audit — Session 5108

Candidate: companion `osEepromLongRead = 0x8002A120`.

- The companion symbol file supplies the semantic name and address.
- The generated snapshot contains no `func_8002A120` or
  `fake_func_8002A120` prologue/body. It contains only the host-wrapper
  declaration and calls to `osEepromLongRead_recomp`.
- `recomp_overlays.inl` records `osEepromLongRead_recomp` at offset
  `0x29CE0` with `rom_size = 0`, confirming this is an externally implemented
  wrapper rather than a generated text span. The following wrapper entry is
  at `0x29D70`.
- Three independent generated callers exist in `funcs_2.c`, at guest callsites
  `0x800064F8`, `0x800069C0`, and `0x80006B44`.
- The bounded companion helper selected no generated rename and reported the
  candidate as already synchronized under its placeholder-only policy.

The host ABI name remains `osEepromLongRead_recomp`; changing it would require
coordinated runtime-wrapper and generated-call edits, not a generated-symbol
rename. This candidate therefore selects the host-wrapper hypothesis. No
build or soak was run.
