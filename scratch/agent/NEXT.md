# NEXT work unit — audit `data_gap_800BEBFC`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved project-TOML placeholder, `data_gap_800BEBFC`, in
the mission overlay. Compare its companion symbol entry, generated body,
callers, header, overlay registration, project TOML, and local duplicates.
Rename only if an exact semantic identity is independently supported (two
sources); otherwise record why it remains a data gap. This is one bounded
static audit and requires no build or runtime run.

## Competing hypotheses

- H-ExactIdentity: an independent source identifies this record as a named
  function or preamble, permitting a regeneration-safe TOML sync.
- H-DataGap: no independent second source names this record; it remains
  a preserved data-gap placeholder.
- H-MappingDrift: companion and generated/project metadata disagree on
  address or extent.

## Discriminating measurement

Check the companion oracle `build/redefs.txt` and source/m2c material for an
independent name for `data_gap_800BEBFC`. If present with a semantic name,
select H-ExactIdentity and sync the TOML. If absent, confirm H-DataGap and
advance the sweep cursor to the next unresolved candidate after
`0x800BEBFC` in VRAM order. Any address/extent mismatch selects
H-MappingDrift.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `grep -n "800BEBFC\|data_gap_800BEBFC" /Users/williambuckley/Documents/Tools/rogue_squadron64/build/redefs.txt | head -10`
3. `grep -n "800BEBFC" /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt`
4. `grep -n "800BEBFC\|data_gap_800BEBFC" /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/rename_generated_symbols.py`
5. Locate generated body/header/registration surfaces with `rg`, then record
   the six-surface comparison in `scratch/agent/s<next>_generated_symbol_rename/AUDIT.md`.
