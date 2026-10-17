# Generated-symbol audit: `osCreateViManager`

Session 5219 (2026-10-17) audited `osCreateViManager = 0x80034DB0`.

The bounded `rename_generated_symbols.py` pass reported `already-synchronized`
and renamed zero references in zero files. The generated tree contains the ABI
declaration, one generated caller, and a zero-size overlay record, but no
generated body or placeholder at the companion address. The companion map
places `osVirtualToPhysical` at `0x80035120`, so the nominal span is `0x170`,
but no body exists to validate it.

This selects the unmaterialized libultra/ABI outcome. Preserve the existing
semantic name. It rules out a generated-symbol rename and a body/span mismatch
for this candidate, but makes no runtime claim.
