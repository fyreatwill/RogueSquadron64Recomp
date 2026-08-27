# NEXT work unit (s2747) — continue the generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Select one adjacent bounded address region containing a verified rename batch
from existing `tools/rename/build_redefs.py` mappings or a previously audited
semantic boundary. Apply it to `../N64Recomp/RecompiledFuncs` with the
fail-closed helper. Do not invent names from implementation shape, regenerate
the whole tree, or run the game.

## Competing hypotheses and discriminator

- H-verified-fragments-remain: the next region contains existing, defensible
  mappings whose generated placeholders can be renamed.
- H-already-synchronized: companion names exist, but generated references in
  the region already use them.
- H-ambiguous-or-fake: only fake/address-only fragments remain and no audited
  semantic mapping is available.

The discriminator is the complete candidate table for one bounded region:
each candidate must be selected, already synchronized, or preserved as
ambiguous-or-fake. A selected candidate must produce a nonzero generated-file
diff; otherwise choose another adjacent region before stopping.

## Exact commands

1. Check the last 15 ledger titles:
   `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. Inspect the next adjacent region and existing mappings without writing:
   `python3 - <<'PY'` using `tools/rename_generated_symbols.py`'s
   `companion_renames` over the selected address interval.
3. Apply one bounded batch:
   `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --start-address START --end-address END --limit 32 --require-rename`
4. Verify the old names are absent and the new names occur in the expected
   generated files; record the full decision table in a new scratch artifact.

Expected outcomes: a nonzero rename selects H-verified-fragments-remain and
lands a generated-symbol change; zero selected candidates selects either
H-already-synchronized or H-ambiguous-or-fake and requires moving to the next
adjacent region in this same work unit.
