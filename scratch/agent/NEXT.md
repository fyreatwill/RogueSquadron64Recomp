# NEXT work unit (s2671) — run the qualified Step 1 contract rebaseline

HYPOTHESIS-ID: m5-audio-step1-contract-rebaseline

## Work unit

Use the now-qualified `s2285` phase driver for the existing same-build
silent/image contract comparison. Collect the oracle controls and both arm
summaries through title and hangar, including task fields, DMEM/DMA, SP
completion, image-stage, PCM source/consumer, and terminal markers. Do not
alter runtime behavior, audio routing, gates, writeback, or guards.

## Competing hypotheses and discriminator

- `H-contract-separated`: oracle, title, and hangar controls pass; image has
  the expected DMEM/DMA/SP work while silent has the zero-work control, so the
  downstream output edge is measurable.
- `H-contract-not-separated`: both arms reach the phases but the expected
  image/silent task-work separation is absent, leaving the contract mapping
  unresolved.
- `H-step1-control-invalid`: the oracle, title/hangar, or arm controls fail,
  so the comparison is unevaluable.

The discriminator is one same-build table: oracle whole-RDRAM/title/hangar
controls; title/hangar rows for both arms; silent versus image DMEM/DMA/image
stage/SP separation; and task/PCM joins. Expected work separation with both
hangar rows selects `H-contract-separated`; absent separation selects
`H-contract-not-separated`; missing controls selects `H-step1-control-invalid`.

## Exact commands

1. `zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s2671_m5_step1_contract_rebaseline`
2. Inspect only its `driver.log` and bounded `grep -c`/`tail -50` slices of
   the arm logs.

Expected: the oracle positive control and both hangar rows remain present;
image shows DMEM/DMA/SP work while silent supplies the zero-work control.
