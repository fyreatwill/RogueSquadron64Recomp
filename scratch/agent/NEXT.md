# NEXT work unit (s2881) — generated-symbol-renaming-sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Continue the generated-symbol renaming sweep starting at `0x800AF700`. Run
the rename script in discovery mode over a bounded interval, classify each
placeholder record (data-gap, callable-ambiguous, or source-backed name), and
rename only records with mechanical proof or companion-backed semantic names.

## Competing hypotheses and discriminator

- H-data-gap: the placeholder in the interval covers non-callable data bytes
  (proven by `__builtin_trap()` fixup annotation, or by fewer than 2 useful
  instructions with no caller).
- H-callable-ambiguous: the record has executable instructions but no
  source-backed name; leave unchanged.
- H-source-backed: the companion provides a semantic name matching the
  generated body; rename unconditionally.

The discriminating deliverable is a source table (`source-table.md` in the
session scratch directory) mapping each candidate to one of these three
classifications, with evidence cited for each rename decision. An unchanged
entry requires a stated reason; an unnamed reason is not a reason.

## Exact next commands

1. Find the next unresolved placeholder after `0x800AF700`:
   ```
   python3 tools/rename_generated_symbols.py \
     --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
     --start-address 0x800AF700 \
     --end-address 0x800B4000 \
     --limit 10 \
     /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/
   ```
2. For each `ambiguous-or-fake` candidate: read 20 lines of context around
   the function body in RecompiledFuncs/; check the overlay rom_size; check
   for callers (`grep -rn "fake_func_ADDR"`); classify.
3. Rename only mechanically-proven data-gaps or companion-named callables;
   add entries to the RENAMES dict in `tools/rename_generated_symbols.py`.
4. Apply: re-run `rename_generated_symbols.py` with `--start-address` and
   `--end-address` scoped to the renamed entries.
5. Write source table to `scratch/agent/s2881_generated_symbol_rename/source-table.md`.

## Expected discriminating outcomes

- Zero renames found → document as such and advance the start address; NOT
  ADVANCED-worthy alone; pivot to a different range or a different angle.
- One or more renames → engineering change lands; ADVANCED. Session entry
  must name H-data-gap SELECTED or H-source-backed SELECTED for each rename.
- All ambiguous → document as such; ADVANCED only if the source table is new
  evidence. Do not rename callable-ambiguous entries.
