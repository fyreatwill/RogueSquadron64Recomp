# Next work unit (s4361): compare joined task payload with selector fields

HYPOTHESIS-ID: m5-selector-decode-boundary

The qualified s4360 retail oracle capture passed whole-RDRAM and both target
phase controls. A bounded range table retained 512 rows in each title origin
(`0x00790400`, `0x00790800`) and hangar origin (`0x006AB400`). In all buckets,
`0x80033FCC` received `$a0=0x80149470` with `MEM_W($a0)=2`; the C904/C950
join was live. The prior zero at this PC was an instrument-boundary result.

Competing hypotheses:

- H-pre-filter-origin: the joined task payload/data block already disagrees
  with the C904/C950 input or selected fields.
- H-consumer-transform: the joined task payload agrees with the selector inputs,
  and divergence is introduced after the task consumer.
- H-selector-multiplex: the same type-2 task is shared, but phase/source-keyed
  payload words identify a separate selector branch before output decode.

Discriminating measurement: add one phase-keyed bounded dump at the live
`0x80033FCC` task rows that records the task `data_ptr` block words alongside
the latest C904/C950 input words, selected address/word, and branch fields;
retain all three phase buckets and the whole-RDRAM/C904/C950/VI controls. A
joined payload/input disagreement selects H-pre-filter-origin; agreement with
later-only divergence selects H-consumer-transform; phase-specific payload
families with shared task identity select H-selector-multiplex.

Expected commands: extend `tools/oracle/rs64_oracle.c` with the joined payload
dump, run `./tools/oracle/build.sh`, then repeat the verified s4360 Rice recipe
from the repo root for 75 seconds with Start presses at 6,11,...,56 seconds,
capturing to `scratch/agent/soak_results/s4361_payload_compare.log`. Keep
`--watch-write 0x0:0x800000`, the three `--pc-phase-log-width` buckets,
`--watch-pc 0x80033fcc`, `--pc-task-dump 0x80033fcc`, `--c904-witness`,
`--c904-task-join`, and `--vi-trace`. Discard any run lacking the positive
control or title and hangar VI origins.
