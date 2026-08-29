# Session 3069 — `data_gap_800BCC38`

## Discriminator

The competing hypotheses were:

- `H-ExactIdentity`: an independent source names the record as a callable
  function or preamble, permitting a regeneration-safe rename.
- `H-DataGap`: the record is a decoder/data-boundary fragment and should keep
  its explicit data-gap placeholder.
- `H-MappingDrift`: the companion and generated/project metadata disagree on
  address or extent.

The discriminator was the six-surface comparison: companion map and redefs,
generated body and callers, generated header/overlay registration, project
TOML/tooling, and local duplicates.

## Surface comparison

| Surface | Finding | Result |
|---|---|---|
| Companion symbol map | `rogue_squadron64/symbol_files/mission_overlay.txt` defines `data_gap_800BCC38 = 0x800BCC38`; its following comment says the real function is `playerT16Init`, which starts at `0x800BCC40` | Explicit data-gap boundary; no independent preamble name |
| Companion redefs | `build/redefs.txt` maps `func_800BCC38`, `D_800BCC38`, and `fake_func_800BCC38` to `data_gap_800BCC38`; the independent function identity is `func_800BCC40`/`playerT16Init` | H-ExactIdentity has no callable name for `0x800BCC38` |
| Generated body | `N64Recomp/RecompiledFuncs/funcs_32.c` emits an 8-byte `bc1f L_800BCC6C` plus delay-slot `nop`; the branch target is inside `playerT16Init`, and the generated body contains an unresolved cross-function-label trap | Non-callable split/decoder fragment, not a standalone function |
| Generated callers | No generated call targets `0x800BCC38`; the two callers in `funcs_32.c` call `playerT16Init` at `0x800BCC40` | No evidence for a callable entry at the gap |
| Header / overlay registration | `funcs.h` declares `data_gap_800BCC38`; `recomp_overlays.inl` registers it at offset `0x17B08`, size `0x8`, immediately before `playerT16Init` at `0x17B10`, size `0x234` | Generated metadata agrees with the 8-byte boundary and extent |
| Project TOML / tooling / duplicates | `syms/rogue_squadron.syms.toml` has `data_gap_800BCC38`, VRAM `0x800BCC38`, size `0x8`; `rename_generated_symbols.py` preserves the same mechanical mapping; no local duplicate supplies a semantic identity | No mapping drift or supported rename |

## Decision

`H-DataGap` selected. The companion comment identifies the adjacent real
initializer, but `redefs.txt` independently assigns that identity only to
`0x800BCC40`. The generated 8-byte record branches into the initializer's
body and is not called by generated code; its unresolved cross-function label
is evidence of a decoder boundary rather than a missing semantic function
name. All live naming, extent, and registration metadata agree, so
`H-MappingDrift` is rejected. Preserve `data_gap_800BCC38`.

No build or runtime run was needed for this static unit. The next unresolved
mission-overlay candidate is `data_gap_800BEBFC`.

ORIGIN: naming-only classification. No runtime, generated instruction, route,
audio, or submodule behavior changed.
