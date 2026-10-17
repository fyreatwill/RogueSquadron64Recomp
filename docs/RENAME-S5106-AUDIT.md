# Generated-symbol rename audit: `bcmp`

The bounded sweep selected the companion entry `bcmp = 0x80029F60` from
`rogue_squadron64/symbol_files/libultra.txt`.

- The generated function began as `bcmp_recomp` at `0x80029F60` in
  `N64Recomp/RecompiledFuncs/funcs_7.c`.
- `recomp_overlays.inl` gives it ROM offset `0x29B20` and span `0x120`; the
  next entry, `bzero_recomp`, begins at `0x29C40`, so the generated span ends
  exactly at the companion function boundary.
- One generated live caller exists at `funcs_2.c:2619`, reached from the
  `0x80006558` call site.
- The body is a byte-comparison routine: it compares aligned words and
  handles the short/misaligned tails before returning the comparison result.

The address, exact span, semantic role, and live caller agree. The generated
tree and overlay table were renamed from `bcmp_recomp` to `bcmp`; the rename
tool now records the non-placeholder address separately so a bounded run can
select this libultra mapping without treating the `_recomp` suffix as an
address.
