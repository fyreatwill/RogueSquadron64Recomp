# NEXT work unit (s2296) — M5 target/output writer-PC role join

HYPOTHESIS-ID: m5-step3-retail-task-output-writer

## Work unit

Run one oracle-only retail capture using the corrected s2295 route and
controls. Retain watch indexes 0=`0x0:0x800000`, 1=`0x166000:0x16A000`,
2=`0x141AD0:0x141AF0`, and 3–18 the 16 exact `0x300` ring slots. Retain
`--watch-pc 0x800078EC`, `--pc-phase-log-width 0x006AB400:512`,
`--pc-hist-phase 0x006AB400:512`, `--pc-hist-watch 2`, `--post-value-watch 2`,
`--vi-trace`, `--hit-cap 200`, and the eleven named Start presses. Replace
the prior post-value-PC request with
`--post-value-pc 0x8008EB8C,0x8008EBBC,0x80094648` so the oracle emits bounded
target address/value rows for each observed target-phase writer. Do not
launch a port arm and do not implement a writer, writeback, consumer, slot,
gate, guard, or address remap.

## Competing hypotheses and discriminating measurement

- H-TaskOutputSemanticEB8C: only `0x8008EB8C` has unique non-sentinel
  target address/value rows; the other two PCs are setup or housekeeping.
- H-TaskOutputSemanticEBBC: only `0x8008EBBC` has unique non-sentinel
  target address/value rows; the other two PCs are setup or housekeeping.
- H-TaskOutputSemantic94648: only `0x80094648` has unique non-sentinel
  target address/value rows; the other two PCs are setup or housekeeping.
- H-TaskOutputSharedOrMulti: two or more PCs have non-sentinel target rows,
  or all three join the same address/value sequence, so this measurement
  cannot assign one semantic publisher.

The discriminator is one table keyed by `(writer PC, target-row count,
target VI/origin, address, value, nonzero/sentinel class)`, from the
`post-target-row-final` records. The whole-RDRAM threshold, title, hangar,
and positive `width=512, origin=0x006AB400` bucket must all be present first;
otherwise record H-CoverageInvalid and do not interpret writer rows.

## Exact commands

1. Create the self-contained driver
   `scratch/agent/run_s2296_m5_target_output_writer_pc_join.sh` from the
   corrected s2295 driver, changing only the output directory/name and
   `--post-value-pc` argument to
   `0x8008EB8C,0x8008EBBC,0x80094648`. Add a bounded summary of each
   `post-target-row-final` PC/address/value table and a verdict using the
   hypotheses above.
2. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2296_m5_target_output_writer_pc_join.sh`

   `zsh scratch/agent/run_s2296_m5_target_output_writer_pc_join.sh`

If any independent control or the width-512 target bucket is absent, record
H-CoverageInvalid and do not interpret a writer null.
