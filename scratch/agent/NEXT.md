# Next work unit (s4316): compare the requalified retail and port consumer streams

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4315): the retail route is qualified again with Rice video, eleven
documented Start presses, the whole-RDRAM control, and the 1024->512 transition
at 38.4 s to origin `0x006AB400`. The consumer-PC watch hit 604 times and the
first hangar-phase consumer chain again contains `0x17D9E0 -> 0x8017D9F8`.
The port side remains qualified at 16,384 rows.

Competing hypotheses:

- H-port: the port's first 16,384 keyed rows are not stable under the current seeded route.
- H-layout: retail and port agree at the first boundary but diverge later in stream layout/order.
- H-filter: the retail detail rows include unrelated target-block traversal after the consumer chain.

Discriminator: extract the first 16,384 rows from the requalified retail
detail log's consumer-read chain and join them to the qualified port table by
ordinal `(PC,address,value)`. The first mismatch selects H-layout if it is a
real consumer row; rows that only occur outside the consumer chain select
H-filter. A missing control, hangar origin, or consumer-PC hit invalidates the
comparison.

Use `scratch/agent/s4315_oracle.log` plus the qualified port table; do not add
another diagnostic field or mitigation.
