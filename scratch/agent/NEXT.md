# Next work unit: census the next source-span writer class

HYPOTHESIS-ID: m5-source-writer-census

The immediate-writer boundary selected H2: `0x800078EC` produced 816
mismatch-free zero scalar stores, but none in the exact `0x006AB400:512`
bucket. The next bounded census is the ranked pre-existing source-span writer
`0x80007670`, retaining the same independent controls before any null is used.

Competing hypotheses:

- H1: `0x80007670` has mismatch-free nonzero stores in the exact hangar bucket
  and is the target producer.
- H2: `0x80007670` appears only before or outside the exact hangar bucket, so
  this class is not the target producer; continue the ranked census.
- H3: retail or port misses a required control/target phase, making this class
  unevaluable.

Discriminating measurement: in one run, require retail whole-RDRAM,
title-1024, and hangar-512 controls; collect source-range writer histograms
and mismatch-free scalar rows for `0x80007670` plus its known caller/neighbor
class, separately for the exact `0x006AB400:512` bucket and all other phases.
H1 requires an exact-bucket nonzero scalar row; H2 is a qualified exact-bucket
null with the controls passing; H3 is any missing control or target phase.

Commands:

```sh
cp scratch/agent/run_s3941_m5_candidate_writers.sh scratch/agent/run_s4062_m5_source_writer_07670.sh
${EDITOR:-vi} scratch/agent/run_s4062_m5_source_writer_07670.sh
zsh scratch/agent/run_s4062_m5_source_writer_07670.sh
grep -a -E 'positive-control|origin=0x00790400|origin=0x006AB400|0x80007670|post-store-scalar|post-target' scratch/agent/s4062_m5_source_writer_07670/retail.log | tail -160
```

Keep all three PC watches and the phase-scoped budgets in the single run; do
not infer a writer null from a route that misses either target phase.
