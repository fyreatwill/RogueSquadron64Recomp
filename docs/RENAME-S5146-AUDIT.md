# Session 5146 generated-symbol audit

Candidate: `__osPfsDeclarePage = 0x8002F064`.

- The generated body begins at `0x8002F064` in `funcs_8.c` and its next
  generated entry begins at `0x8002F2C8`, giving an exact `0x264` span.
- `recomp_overlays.inl` records the same entry with `rom_size = 0x264`.
- The companion symbol file maps the address to `__osPfsDeclarePage`.
- The generated-tree search found only the function definition, with no
  independent generated caller.
- The rename helper reported `already-synchronized` and made zero edits.

Classification: preserve the existing ABI name. The body/span gates pass, but
there is no live generated caller supporting a rename, and the semantic name
is already present.
