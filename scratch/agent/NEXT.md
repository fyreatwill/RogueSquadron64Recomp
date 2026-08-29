# NEXT work unit — audit `fake_func_800B75C4`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved project-TOML placeholder, `fake_func_800B75C4`,
which is in the mission overlay immediately before `playerYwingInit` at
`0x800B75D0`. Compare its companion symbol entry, generated body, callers,
header, overlay registration, project TOML, and local duplicates. Rename
only if an exact semantic identity is independently supported (two sources);
otherwise record why it remains a placeholder/data-gap name.
This is one bounded static audit and requires no build or runtime run.

Note: session 2963 previously preserved this entry as H-Fragment. Re-audit
to confirm whether oracle redefs.txt or renamed-tool evidence now provides
an independent preamble name for `0x800B75C4`. For `0x800B58B4` the oracle
redefs.txt had `playerAwingInitPreamble` (line 10116); check whether the
same applies to `0x800B75C4`. If the oracle does NOT have an independent
name, confirm H-Fragment and advance to the next unresolved candidate.

## Competing hypotheses

- H-ExactIdentity: oracle redefs.txt or companion companion evidence now
  independently names this record `playerYwingInitPreamble` (or similar),
  permitting a regeneration-safe TOML sync.
- H-Fragment: no independent second source names this record; it remains
  a preserved placeholder (same decision as s2963).
- H-MappingDrift: companion and generated/project metadata disagree on
  address or extent.

## Discriminating measurement

Check the companion oracle `build/redefs.txt` for a `fake_func_800B75C4`
entry. If present with a semantic name, select H-ExactIdentity and sync
the TOML. If absent, confirm H-Fragment and advance the sweep cursor to the
next unresolved candidate after `0x800B75C4` in VRAM order.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `grep -n "800B75C4\|playerYwingInitPreamble\|YwingInit" /Users/williambuckley/Documents/Tools/rogue_squadron64/build/redefs.txt | head -10`
3. `grep -n "800B75C4" /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt`
4. `grep -n "800B75C4\|playerYwingInitPreamble" /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/rename/build_redefs.py`
5. Record the six-surface comparison in
   `scratch/agent/s<next>_generated_symbol_rename/AUDIT.md`.
