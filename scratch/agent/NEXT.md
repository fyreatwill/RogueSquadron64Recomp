# NEXT work unit (s2706) — bounded generated-symbol rename lead

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the required last-15-title revisit check. If it still does not force a
revisit, reconcile the next adjacent companion-symbol region
`0x80095000..0x80098000` with the bounded rename tool. Rename only exact,
unique generated placeholders supported by the companion map; preserve fake,
ambiguous, and already-human names. This is one bounded rename batch, not a
whole-tree census.

## Competing hypotheses and discriminator

- `H-exact-matches`: the selected region has unique companion names that are
  not synchronized into the generated snapshot.
- `H-already-synchronized`: every companion name in the region is already
  present or intentionally address-only in generated output.
- `H-ambiguous-or-fake`: candidates lack unique semantic evidence and must be
  preserved.
- `H-tool-rejects`: the tracked tool cannot represent a valid candidate or
  rejects the batch for a parser/duplicate-destination defect.

The discriminator is the tool's complete per-candidate decision table plus
the generated diff: a non-empty exact rename selects `H-exact-matches`; zero
selected with explicit synchronized/ambiguous reasons selects the applicable
zero-result hypothesis; a reproducible parser or destination rejection
selects `H-tool-rejects` and requires fixing it in this iteration.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. Inspect the tracked rename-tool usage: `sed -n '1,260p' tools/rename/README.md` and `rg -n 'argparse|region|mapping|placeholder|duplicate|redef' tools/rename/rename_generated_symbols.py tools/rename/build_redefs.py`.
3. Run:
   `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --limit 32 --start-address 0x80095000 --end-address 0x80098000`
   and capture its decision table under
   `scratch/agent/s2706_generated_symbol_sweep/`.
4. Verify the generated diff and exact unique companion/source evidence; do
   not build or run the game unless a real rename changes generated code.

The previous M5 unit found no indirect producer and no legitimate AI
destination edge, so no M5 runtime watch or mitigation is authorized here.
