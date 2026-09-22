# Next work unit: M5 retail source-payload boundary

HYPOTHESIS-ID: m5-retail-source-payload-boundary

Session 3728 selected `H-ImageProducerZero` only at the port boundary. The
retail oracle reached the same target task path, but the run did not measure
retail payload bytes or writer attribution. Do one ground-truth oracle run
before any port behavior change.

Competing hypotheses:

- `H-RetailSourceZero`: retail's image-task source span is legitimately zero
  at the target task boundary, matching the port.
- `H-RetailSourceNonzero`: retail writes nonzero source/task data before the
  image task, so the port's producer path is divergent.
- `H-RetailOutputOnly`: retail source is zero but a separate output producer
  supplies nonzero destination data.

Discriminator: in one oracle run, arm the whole-RDRAM positive control plus
phase-gated writer watches/histograms for the retail source span around
`0x1797B0..0x179A48`, task-data spans observed at `0x80171E70`/`0x80173CB0`,
and the known output windows around `0x166450..0x169450` and
`0x1935E0..0x193778`. Retail nonzero source/task writes select
`H-RetailSourceNonzero`; zero source with nonzero output writers selects
`H-RetailOutputOnly`; zero values and no nonzero writer in both spans select
`H-RetailSourceZero`. The whole-RDRAM watch and target VI/task execution are
positive controls; a missing target phase is unevaluable.

Exact command basis: adapt
`scratch/agent/run_s3728_m5_image_payload.sh`'s oracle invocation, retaining
`--watch-write 0x0:0x800000`, Rice video, the validated Start schedule,
`--pc-task-dump 0x80033FCC`, and both target `--pc-phase-log-width` buckets;
add the source/task/output watches and `--pc-hist-phase`/`--post-value-watch`
for each target range. Save the result under
`scratch/agent/s3729_retail_source_payload/`, then write
`docs/M5-S3729-*.md`.
