# Generated-symbol audit: `osVirtualToPhysical`

Session 5220 (2026-10-17) audited `osVirtualToPhysical = 0x80035120`.

The bounded `rename_generated_symbols.py` pass reported `already-synchronized`
for both `osVirtualToPhysical` and the next in-range companion
`__osProbeTLB = 0x800351A0`; it renamed zero references in zero files. The
generated tree contains the ABI declaration, seven generated callers in
`funcs_8.c`, and a zero-size overlay record, but no generated body or
placeholder at the companion address. The primary companion map places
`osViSetEvent` at `0x80035260`, so the nominal primary span is `0x140`, but
there is no body to validate it; `__osProbeTLB` is the next bounded sweep
candidate.

This selects the unmaterialized libultra/ABI outcome. Preserve the existing
semantic name. It rules out a generated-symbol rename and a body/span mismatch
for this candidate, but makes no runtime claim.
