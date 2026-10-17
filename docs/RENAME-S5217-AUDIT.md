# Generated-symbol audit: `osViBlack`

Session 5217 (2026-10-17) audited `osViBlack = 0x80034BE0`.

The bounded `rename_generated_symbols.py` pass reported `already-synchronized`
and renamed zero references in zero files. The generated tree contains only
the ABI declaration in `funcs.h`, two call sites from `funcs_0.c`, and a
zero-size overlay record in `recomp_overlays.inl`; it contains no generated
body or placeholder at the companion address. The companion map places
`osViGetCurrentField` at `0x80034D90`, but that nominal span cannot be
validated without a body.

This selects the unmaterialized libultra/ABI outcome. Preserve the existing
semantic name. It rules out a generated-symbol rename and a body/span
mismatch for this candidate, but makes no runtime claim.
