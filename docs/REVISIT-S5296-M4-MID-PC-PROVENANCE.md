# Session 5296 M4 retail mid-task PC provenance

The qualified retail capture from `scratch/agent/s5279_m4_acc_boundary/` was
reanalyzed without a new runtime build or soak. The parser checks every 68-byte
`RSM1` record and the independent `RSD1` completion stream.

Controls passed:

- 3,036,036 `RSM1` records, all valid, task type 1, with contiguous sample
  ordinals `0..3,036,035`.
- 6,533 valid `RSD1` records, including 2,085 graphics records.
- The end-of-task stream has zero `0x8000` lanes in all 2,085 graphics records.

Retail mid-task state has 367,023 sampled `0x8000` lanes across 125,080
sample records. The samples are not concentrated at one PC: the largest PC
buckets are `0x0B18` (25,152), `0x0B20` (24,344), `0x0B1C` (23,600),
`0x0B34` (23,320), and `0x0B14` (23,128), with additional populated PCs.
This rejects the narrow hypothesis that the observed value is attributable to
one uniquely sampled PC.

The `RSM1` sequence field is a global sample ordinal, not a graphics-task ID;
therefore this capture cannot establish per-task prevalence or join a mid-task
sample to an `RSD1` task. The result is valid sample-level retail provenance,
but the task-level publication/order boundary remains unevaluable. This is
single-source oracle evidence with an independent end-of-task positive-control
stream, not a port-side explanation.

The next M4 unit should add an explicit task serial to the cxd4 mid-task record
and rerun the same qualified route, or otherwise obtain a task-keyed join. No
mitigation or accumulator rewrite follows from this result.
