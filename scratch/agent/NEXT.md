# Next work unit: close the immediate-writer phase boundary

HYPOTHESIS-ID: m5-immediate-zero-writer

The prior capture qualified both target phases and the port zero-payload
signature, but exact hangar-phase requested-PC rows were empty. Its 816
zero-valued `0x800078EC` scalar stores were tagged to transition
`0x006AB800/1024`, so the next unit must split transition and exact-hangar
evidence in one run before naming a replacement producer. Before changing any
instrumentation, retain the retail whole-RDRAM positive control and verify that
it passes in this capture.

Competing hypotheses:

- H1: exact hangar rows appear for `0x800078EC` with zero scalar values and a
  matching `0x800078E0` tuple; this is legitimate target-phase padding.
- H2: exact hangar rows remain absent while transition rows are attributed to
  `0x800078EC`, proving the prior hit was a phase/argument match; any target
  producer must be a different PC/tuple or absent.
- H3: either retail or port misses a required positive control/target phase, so
  all writer nulls are unevaluable.

Discriminating measurement: in one run, require retail whole-RDRAM,
title-1024, and hangar-512 controls; collect source-range writer histograms
and scalar rows for both explicit buckets `0x006AB800:1024` and
`0x006AB400:512`, plus entry/predecessor tuples for all three PCs. H1 is
selected only if the exact hangar bucket contains matching zero-valued
`0x800078EC`/`0x800078E0` rows. H2 is selected if only the transition bucket
contains `0x800078EC`, or if the exact hangar bucket attributes a different
writer/tuple. H3 is selected if either paired route misses a required control.

Commands:

```sh
cp scratch/agent/run_s3941_m5_candidate_writers.sh scratch/agent/run_s4061_m5_immediate_zero_boundary.sh
${EDITOR:-vi} scratch/agent/run_s4061_m5_immediate_zero_boundary.sh
zsh scratch/agent/run_s4061_m5_immediate_zero_boundary.sh
grep -a -E 'positive-control|origin=0x00790400|origin=0x006AB800|origin=0x006AB400|0x800C825C|0x800078E0|0x800078EC|post-store-scalar|post-target' scratch/agent/s4061_m5_immediate_zero_boundary/retail.log | tail -160
```

Keep all three PC watches and the phase-scoped budgets in the single run; do
not infer a writer null from a route that misses either target phase.
