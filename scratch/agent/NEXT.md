# Next work unit (s4386): detail the live hangar writers

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-hangar-selector-writer: post-values from live hangar writers
  `0x8008F7D4` or `0x80091374` recur in the phase-matched published payload
  after publication.
- H-hangar-maintenance: both writers are live and scalar-valid, but their
  post-values have zero equality with the phase/task-keyed payload writes.
- H-hangar-value-watch-gap: the corrected writer rows are absent, unsupported,
  mismatched, or still overflowed.

Discriminating measurement: run one retail-oracle capture with detail enabled
for only `0x8008F7D4,0x80091374`, retain task publication ordinals and payload
range writes, and join each writer post-value by phase/address/ordinal to the
nearest type-2 payload write. Nonzero exact equality selects the selector
writer; live scalar-valid rows with zero equality select maintenance; absent or
unsupported rows select a remaining watch boundary. Do not interpret the
ordinal `equal` field by itself as payload equality.

Ground-truth controls required in the same run: whole-RDRAM writes, title
origins `0x00790400:1024` and `0x00790800:1024`, hangar origin
`0x006AB400:512`, at least 1,000 valid type-2 rows, zero ordinal overflow, and
`mismatch=0` for both requested writers. The s4385 positive controls passed;
its detail table overflowed because it requested the stale large PC list.

Exact commands:

    bash tools/oracle/build.sh
    apply the s4385 runner's output directory and replace its
    --post-value-pc list with 0x8008F7D4,0x80091374
    scratch/agent/run_s4386_m5_hangar_writer_payload.sh

Use `scratch/agent/s4385_m5_hangar_writer_payload/oracle.log` as the runner
template, write the new runner with `apply_patch`, and keep the 75-second Rice
route, phase schedule, task watch, `--ordinal-join`, both payload watches, and
`--post-value-pc-detail` unchanged. Summarize controls and equality counts
from bounded `rg`/`sed` windows; never read the full log.
