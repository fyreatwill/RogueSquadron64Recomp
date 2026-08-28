# NEXT work unit (s2874) — generated-symbol-renaming-sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Inspect and, only if source-backed, rename the next two short main-overlay
placeholder records at `0x8007A86C` and `0x8007C298` to explicit `data_gap_*`
names. Propagate through the companion map, project TOML map, generated C
snapshot, declarations, and overlay registry. Leave any callable or ambiguous
record unchanged.

## Competing hypotheses and discriminator

- H-callable: a placeholder body is a real callable function and must remain
  unresolved rather than receive a data-gap name.
- H-data-gap: the body is an isolated short instruction fragment between named
  functions and can be renamed mechanically.
- H-mapping-drift: companion and generated addresses or sizes disagree; stop
  without editing that entry.

The discriminator is one bounded source table containing each body's exact
byte size/instructions, neighboring named boundaries, and companion
classification. A short fragment with no return/prologue selects H-data-gap;
callable structure selects H-callable; any address/size mismatch selects
H-mapping-drift.

## Exact command

    python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x8007A86C --end-address 0x8007C2A0 --limit 2 --require-rename

Verify with `python3 -m py_compile tools/rename_generated_symbols.py`, exact
reference counts, and `git diff --check`. Record the source table under
`scratch/agent/s2874_generated_symbol_rename/`.
