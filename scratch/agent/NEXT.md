# NEXT work unit (s2752) — bounded generated-symbol rename batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

The M5 speech-loader surface was audited in
`scratch/agent/s2751_m5_speech_loader/audit.md` and selected service-only:
there is no new source-backed CPU publication edge to de-stub. Resume the
generated-symbol sweep with one bounded source-backed batch. Before changing
anything, run the required revisit check; the last 15 ledger titles are not
all sweep titles, so the sweep remains eligible.

Use the rename tool's companion-backed decision table to select the next
contiguous region, apply only exact source/m2c-backed mappings, and preserve
address-only, fake, and ambiguous symbols. This is a real rename change, not a
diagnostic census.

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
   `scratch/agent/s2752_generated_symbol_sweep/`.
