# Session 3199 generated-symbol rename

## Classification

Target `static_3_800A2B50` has no matching companion symbol record. Its
generated body begins with isolated zero-shift decodes, then trap/invalid
instructions, and lacks a standalone callable prologue. This selects
`H-DataGap`; `H-SemanticMatch` and `H-Ambiguous` are not supported for this
record.

## Change and verification

Added the regeneration-safe mapping
`static_3_800A2B50` -> `data_gap_800A2B50` in
`tools/rename_generated_symbols.py`. The bounded helper renamed exactly three
references across `funcs_27.c`, `funcs_49.c`, and `funcs.h`; the generated
overlay table had no occurrence. A final search across `RecompiledFuncs`
found zero stale `static_3_800A2B50` references.

No build or runtime run was needed; this is a source-only naming change.
