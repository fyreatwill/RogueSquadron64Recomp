# Next work unit: census the 0x800076A0 source-span writer class

HYPOTHESIS-ID: m5-source-writer-census

The immediate-writer boundary selected H2 for `0x800078EC`, and session 4062
selected H2 for `0x80007670`: it executed 1,563 times in the hangar source
watch but produced no exact-bucket target row. The next bounded census is the
adjacent ranked source-span writer `0x800076A0`, retaining the same independent
controls before any null is used.

Competing hypotheses:

- H1: `0x800076A0` has mismatch-free nonzero stores in the exact hangar bucket
  and is the target producer.
- H2: `0x800076A0` appears only before or outside the exact hangar bucket, so
  this class is not the target producer; continue the ranked census.
- H3: retail or port misses a required control/target phase, making this class
  unevaluable.

Discriminating measurement: in one run, require retail whole-RDRAM,
title-1024, and hangar-512 controls; collect source-range writer histograms
and mismatch-free scalar rows for `0x800076A0` plus its known caller/neighbor
class, separately for the exact `0x006AB400:512` bucket and all other phases.
H1 requires an exact-bucket nonzero scalar row; H2 is a qualified exact-bucket
null with the controls passing; H3 is any missing control or target phase.

Commands:

```sh
cp scratch/agent/run_s4062_m5_source_writer_07670.sh scratch/agent/run_s4063_m5_source_writer_076A0.sh
${EDITOR:-vi} scratch/agent/run_s4063_m5_source_writer_076A0.sh
zsh scratch/agent/run_s4063_m5_source_writer_076A0.sh
grep -a -E 'positive-control|origin=0x00790400|origin=0x006AB400|0x800076A0|post-store-scalar|post-target' scratch/agent/s4063_m5_source_writer_076A0/retail.log | tail -160
```

Keep all three PC watches and the phase-scoped budgets in the single run; do
not infer a writer null from a route that misses either target phase.
