# Generated-symbol audit: `osViGetCurrentField`

Session 5218 (2026-10-17) audited `osViGetCurrentField = 0x80034D90`.

The bounded `rename_generated_symbols.py` pass reported `already-synchronized`
and renamed zero references in zero files. The generated tree contains a
single call site from `funcs_4.c`, but no generated body, placeholder, header
declaration, or overlay record at the companion address. The companion map
places `osCreateViManager` at `0x80034DB0`, but that nominal `0x20` span cannot
be validated without a body.

This selects the unmaterialized libultra/ABI outcome. Preserve the existing
semantic name. It rules out a generated-symbol rename and a body/span mismatch
for this candidate, but makes no runtime claim.
