# Next work unit (s4311): extend the qualified port free/read join to the later divergence

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4310): the corrected boot-relative seeded-save/key route reached VI 512
at 42.0 s, passed the adjacent-range and phase-gated read positive controls,
and captured 256 target reads plus 256 selected writer rows with 0 mismatches.
The target block `0x8017D910` was freed by `waitForAnyAudioSlot` at guest PC
`0x80095D54` before the hangar phase. The first port read
`0x8008FCE8: 0x17D9E0 -> 0x8017D9F8` matches the independent retail boundary.
Port-only reuse before the first consumer read is therefore ruled out; the
later consumer traversal/layout divergence remains open.

Competing hypotheses:

- H-free-before-consumer: selected at the first-read boundary; the shared free
  precedes the port read and its PC/address/value match retail.
- H-port-reuse-before-consumer: ruled out at that boundary by the free/read
  join and the matched first value.
- H-retail-reclaims-different: remains possible for later traversal/layout;
  the bounded 256-row join does not yet name the first later divergence.

Discriminator: one clean port VI-512 run extending the bounded read/write join
past row 256, with a keyed snapshot at the first read whose PC/address/value
differs from the retail sequence. A divergence after the matched first read
with no intervening port-only writer selects a later consumer/overlay issue;
an intervening port-only writer selects H-retail-reclaims-different. Missing
controls, no VI 512, or a crash before the keyed divergence is invalid. Do not
add a guard or skip.

Before any build, inspect the existing port free/read join and confirm its
positive-control and phase-gating fields. Batch all three hypotheses in one
instrument/build/run; do not make an A/B arm or mitigation.

Expected command family: reuse the successful s4310 boot-relative recipe and
extend the existing bounded rows in one build/run. Retain
`ROGUESQ_LOG_S4306=1`, `ROGUESQ_LOG_S4307=1`, and `ROGUESQ_LOG_RS_FREE=1`, run
from `build/`, kill with SIGKILL, and capture under
`scratch/agent/s4311_port_free_read_join/`. A missing positive control or no
VI 512 is invalid; do not add a guard or skip.
