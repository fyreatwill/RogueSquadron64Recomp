# Next work unit: classify the immediate M5 zero writer

HYPOTHESIS-ID: m5-immediate-zero-writer

Use the already-qualified declared-real port arm and the retail oracle in one
same-build capture. The primary class is guest PC `0x800078EC`; retain
`0x800078E0` and `0x800C825C` as predecessor context. Before changing any
instrumentation, arm the retail whole-RDRAM positive control and verify that it
passes in this capture.

Competing hypotheses:

- H1: `0x800078EC` is the target-phase source-span writer and its zero scalar
  values are legitimate padding/clear input; the missing nonzero payload was
  already absent upstream.
- H2: `0x800078EC` is only a phase/argument match caused by the port-side
  witness, while retail's corresponding target-phase writer has a different
  entry tuple or predecessor that supplies nonzero data.
- H3: the declared-real port arm is not qualified in this capture, so any
  writer null or mismatch is unevaluable rather than evidence for H1/H2.

Discriminating measurement: in the same run, require retail whole-RDRAM,
title-1024, and hangar-512 controls; collect phase-gated scalar rows for
`0x800078EC`, entry rows for `0x800078E0`, and predecessor rows for
`0x800C825C`, including PC, phase, destination offset, value, and call/entry
tuple. H1 is selected only if both retail and port reach the target phases and
the retail target rows attribute zero values to `0x800078EC` with matching
`0x800078E0` arguments. H2 is selected if retail target rows show a distinct
nonzero producer or a tuple mismatch. H3 is selected if either paired route
misses a required control/phase.

Commands:

```sh
cp scratch/agent/run_s3941_m5_candidate_writers.sh scratch/agent/run_s4059_m5_immediate_zero_writer.sh
${EDITOR:-vi} scratch/agent/run_s4059_m5_immediate_zero_writer.sh
zsh scratch/agent/run_s4059_m5_immediate_zero_writer.sh
grep -a -E 'positive-control|origin=0x00790400|origin=0x006AB400|0x800C825C|0x800078E0|0x800078EC|post-store-scalar|post-value' scratch/agent/s4059_m5_immediate_zero_writer/retail.log | tail -120
```

Keep all three PC watches and the phase-scoped budgets in the single run; do
not infer a writer null from a route that misses either target phase.
