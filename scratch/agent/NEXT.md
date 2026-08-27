# NEXT work unit (s2753) — bounded generated-symbol rename batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

The `0x800E7000..0x800E9000` interval was fully synchronized in
`scratch/agent/s2752_generated_symbol_sweep/decision-table.txt`, with fake or
address-only placeholders preserved. Resume the sweep with the next bounded
source-backed batch `0x800E9000..0x800EB000`. Before changing anything, run
the required revisit check; the last 15 ledger titles are not all sweep
titles, so the sweep remains eligible.

Use the companion-backed decision table against the external generated tree
for `0x800E9000..0x800EB000`, apply only exact source/m2c-backed mappings, and
preserve address-only, fake, and ambiguous symbols. This is a real rename
change, not a diagnostic census.

## Competing hypotheses and discriminator

- H2-exact: companion/source evidence maps at least one placeholder to a
  defensible human name and the rename is applied in the generated tree.
- H3-ambiguous: the selected region has candidates but evidence is insufficient
  for a safe rename; preserve them and document why.
- H4-synchronized: the selected region is already synchronized with human
  names, so move to the next bounded region without changing symbols.

The discriminator is the batch decision table: exact companion/source-backed
mappings select H2-exact; all candidates lacking defensible evidence select
H3-ambiguous; a fully synchronized bounded region selects H4-synchronized.
The batch must land either a real rename change or a newly classified bounded
region with the next address interval identified.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`; confirm this is not a
   sweep-only revisit.
2. Inspect the rename tool's next bounded region and companion evidence; do
   not read the full ledger or generated tree.
3. Run the tool's dry-run/decision-table mode, then apply only exact mappings
   from that same table.
4. Verify changed symbols and references, and save the table under
   `scratch/agent/s2753_generated_symbol_sweep/`.
