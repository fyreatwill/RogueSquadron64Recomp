# NEXT work unit (s2975)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Unit

Perform the next bounded generated-symbol rename batch. Inspect unresolved
placeholder records after `0x8009D7CC` in the generated tree and companion
symbol files. Rename only entries with a complete successor boundary and
enough body/caller evidence for a semantic name; leave ambiguous fragments
unchanged. Propagate each selected name through the companion map,
`tools/rename_generated_symbols.py`, and generated C/header/overlay artifacts.

## Competing hypotheses and discriminator

- H-semantic-batch: the next records have defensible companion semantic names
  and can be renamed without changing code behavior.
- H-ambiguous-boundary: the next records are fragments/data gaps without a
  defensible standalone meaning and must remain placeholders.
- H-source-mismatch: the companion map and generated snapshot disagree, so the
  batch must stop until the source-of-truth boundary is reconciled.

The discriminator is one bounded source table containing each candidate
address, generated body shape, successor/predecessor boundaries, companion
name/comment, and generated references. A row with an exact semantic successor
and matching source selects H-semantic-batch; a row lacking that evidence
selects H-ambiguous-boundary; disagreement selects H-source-mismatch. The
rename script must report a positive changed-reference count.

## Commands

1. Enumerate the next placeholders with bounded `rg`/`sed` windows in
   `../N64Recomp/RecompiledFuncs` and `../rogue_squadron64/symbol_files`.
2. Write the candidate table to
   `scratch/agent/s2975_generated_symbol_rename/source-table.md` before edits.
3. Apply one bounded rename batch with
   `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs
   --companion-dir ../rogue_squadron64/symbol_files --start-address ...
   --end-address ... --limit 4 --require-rename`.
4. Build `cmake --build build --target RecompiledFuncs -j2` and verify no
   selected placeholder remains in the generated snapshot.
