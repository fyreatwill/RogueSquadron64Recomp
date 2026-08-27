# NEXT work unit (s2710) — bounded generated-symbol rename lead

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the required last-15-title revisit check. If it still does not force a
revisit, reconcile exactly one adjacent companion-symbol region
`0x800A1000..0x800A4000` with the tracked rename tool. Rename only exact,
unique companion names supported by the companion map; preserve fake,
ambiguous, and already-human names. This is one bounded rename batch.

## Competing hypotheses and discriminator

- `H-exact-matches`: the region contains unique companion names absent from
  generated output.
- `H-already-synchronized`: semantic names in the region are already present.
- `H-ambiguous-or-fake`: candidates lack unique semantic evidence and remain
  address-only.
- `H-tool-rejects`: the tool rejects a valid candidate due to parsing or
  duplicate-destination handling.

The discriminator is the complete per-candidate decision table plus the
generated diff. A non-empty exact rename selects `H-exact-matches`; zero
selected with explicit synchronized/ambiguous decisions selects the relevant
zero-result hypothesis; a reproducible parser or destination rejection
requires fixing the tool in this iteration.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `mkdir -p scratch/agent/s2710_generated_symbol_sweep`
3. `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --limit 32 --start-address 0x800A1000 --end-address 0x800A4000 > scratch/agent/s2710_generated_symbol_sweep/decision-table.txt 2>&1`
4. Verify the decision table, generated diff, and exact unique companion/source
   evidence. Do not build or run the game unless a real rename changes output.

The M5 publication edge remains unresolved; no runtime watch, writeback,
remap, or mitigation is authorized.
