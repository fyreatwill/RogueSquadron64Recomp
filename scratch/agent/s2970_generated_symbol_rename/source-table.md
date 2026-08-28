# Session 2970 source table: `0x8000040C`

| Evidence | Observation | Discriminator result |
|---|---|---|
| Generated bounds | `func_8000040C` occupies `0x8000040C..0x80000440` (`0x34` bytes), immediately after `recomp_entrypoint`'s `0x80000400..0x8000040C` body; `loadOverlay` begins at `0x80000B20`. | Standalone bounded body; not a gap between adjacent callable bodies. |
| Instructions | `beq a1,zero`; computes `(a1+15)>>4`; loops `cache 0x0D,0(t0)`, `sd zero,0(t0)`, `sd zero,8(t0)`, increments by `0x10`; returns. | Callable memory-clear/cache routine, not invalid or data-only bytes. |
| Generated callers | Exactly two calls, both in `main` (`0x80001634` and `0x8000164C`); arguments are caller-supplied base/length values. | Call sites establish use, but not a unique semantic API name. |
| Lookup/reference search | No independent function-pointer lookup, companion caller name, or alternate generated entry was found. | No external naming discriminator. |
| Companion map | `make_elf.py` hardcodes `func_8000040C` as an entry-segment symbol with size `0x34`; no semantic `symbol_files/*.txt` entry exists. | H-named is not selected. |
| Predecessor/successor | The predecessor is the entry wrapper; the next emitted function is `loadOverlay`, with entry-segment strings/data between them. | H-data-gap is ruled out by the complete callable body and callers. |

## Decision

H-ambiguous selected. The routine is genuine callable code, but its address-only
entry-symbol provenance and generic caller-controlled clear/cache behavior do
not support a defensible human name. The placeholder remains unchanged in the
companion map, project TOML, and generated C. `RecompiledFuncs` built
successfully with no symbol changes.
