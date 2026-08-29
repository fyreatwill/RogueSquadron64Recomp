# NEXT work unit — audit `data_gap_800C7DB4`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved project-symbol placeholder, `data_gap_800C7DB4`, in
the mission overlay. Compare its companion symbol entry, generated body,
callers, header, overlay registration, project symbol TOML, and local
duplicates. Rename only if an exact semantic identity is independently
supported; otherwise preserve the mechanical data-gap placeholder. This is
one bounded static audit and requires no build or runtime run.

## Competing hypotheses

- H-ExactIdentity: an independent source identifies a named function or
  preamble, permitting a regeneration-safe TOML sync.
- H-DataGap: no independent second source names this record; preserve the
  mechanical data-gap name.
- H-MappingDrift: companion and generated/project metadata disagree on
  address or extent.

## Discriminating measurement

Check companion `build/redefs.txt` and source/m2c material for an independent
semantic name, then compare all six generated surfaces. A semantic name
supported independently selects H-ExactIdentity; its absence with a coherent
fragment/data boundary selects H-DataGap; any address or extent mismatch
selects H-MappingDrift.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `grep -n '800C7DB4\\|data_gap_800C7DB4' /Users/williambuckley/Documents/Tools/rogue_squadron64/build/redefs.txt | head -10`
3. `grep -n '800C7DB4' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt`
4. `grep -n '800C7DB4\\|data_gap_800C7DB4' tools/rename_generated_symbols.py`
5. `rg -n '800C7DB4|data_gap_800C7DB4' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs syms tools/rename_generated_symbols.py`
6. Record the six-surface comparison in `scratch/agent/s<next>_generated_symbol_rename/AUDIT.md`.
