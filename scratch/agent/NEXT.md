# NEXT work unit — audit `fake_func_800B89F4`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved project-TOML placeholder, `fake_func_800B89F4`,
which is in the mission overlay immediately before `playerVwingInit` at
`0x800B8A00`. Compare its companion symbol entry, generated body, callers,
header, overlay registration, project TOML, and local duplicates. Rename only
if an exact semantic identity is independently supported (two sources);
otherwise record why it remains a placeholder/data-gap name. This is one
bounded static audit and requires no build or runtime run.

Note: the previous sweep audit preserved `fake_func_800B75C4` as a fragment.
Check whether the same oracle redefs/tooling evidence now supplies an
independent preamble name for this V-wing boundary before changing metadata.

## Competing hypotheses

- H-ExactIdentity: oracle redefs.txt or companion evidence independently
  names this record `playerVwingInitPreamble` (or similar),
  permitting a regeneration-safe TOML sync.
- H-Fragment: no independent second source names this record; it remains
  a preserved placeholder.
- H-MappingDrift: companion and generated/project metadata disagree on
  address or extent.

## Discriminating measurement

Check the companion oracle `build/redefs.txt` for a `fake_func_800B89F4`
entry. If present with a semantic name, select H-ExactIdentity and sync
the TOML. If absent, confirm H-Fragment and advance the sweep cursor to the
next unresolved candidate after `0x800B89F4` in VRAM order.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `grep -n "800B89F4\|playerVwingInitPreamble\|VwingInit" /Users/williambuckley/Documents/Tools/rogue_squadron64/build/redefs.txt | head -10`
3. `grep -n "800B89F4" /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt`
4. `grep -n "800B89F4\|playerVwingInitPreamble" /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/rename/build_redefs.py`
5. Record the six-surface comparison in
   `scratch/agent/s<next>_generated_symbol_rename/AUDIT.md`.
