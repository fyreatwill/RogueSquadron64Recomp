# NEXT work unit (s2660) — map the Factor 5 output ABI boundary

HYPOTHESIS-ID: m5-factor5-output-abi

## Work unit

Perform one static Factor 5 ABI census of the generated ucode and its fixup
pipeline: map the task's `data_ptr`, the `data_ptr+0x100` relation, DMEM
source spans, and each `SP_WR_LEN` destination against the s2659 observed
`0x166xxx` and `0x1798B0:0x179A48` ranges. Do not add a task-field watch and
do not change runtime behavior.

## Competing hypotheses and discriminator

- `H-Factor5OutputContract`: the generated image's task/data relation defines
  the observed output spans, and the missing edge is an ABI/data staging
  defect.
- `H-CPU-MORTPublication`: the image spans are only a separate stage; the
  legitimate retail writer belongs to the CPU MORT path.
- `H-GenericStage`: the observed DMA ranges are staging buffers with no PCM
  contract, so neither output hypothesis is supported.
- `H-Unresolved`: the static sources do not identify a complete ownership and
  ordering relation.

The discriminator is one static table keyed by task field/DMEM source/DMA
destination containing source address, length, task-field origin, generated
instruction or fixup site, destination range, and whether the relation is
legitimate PCM or generic staging. A complete `data_ptr+0x100`/DMA mapping
selects `H-Factor5OutputContract`; no relation or a generic-only relation
selects the applicable remaining hypothesis. No build or runtime arm is
required unless the census finds an existing diagnostic source that can be
changed regeneration-safely.

## Exact commands

1. Read `docs/F5-UCODE-REFERENCE.md` and inspect the generated Factor 5
   source/fixup entries for `data_ptr`, `0x100`, and `SP_WR_LEN`.
2. Build no code unless the census identifies a diagnostic source already in
   the fixup pipeline. Do not add another task-field watch.
3. Write the complete table and selected/unevaluable hypothesis to
   `scratch/agent/s2660_m5_factor5_output_abi/audit.md`.

## Expected outcomes

- A complete task/data/DMA relation selects `H-Factor5OutputContract` and
  defines one behavior change with rollback.
- A generic staging relation with no PCM ownership keeps the CPU-MORT edge
  open without changing dispatch.
- Missing/ambiguous static ownership selects `H-Unresolved`; do not implement
  mitigation or writeback.
