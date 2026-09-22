# M5 session 3718 — callback-order qualification

The work unit added a phase-local callback sequence and steady-clock timestamp
to both `[m5-image-queue]` and `[pcm-boundary-consumer]`. The sequence is
assigned under one mutex at the callback boundary and resets at each target VI
origin. The existing phase and RSP-source controls remained enabled.

The build succeeded. The paired run reached title VI 1024 and hangar VI 512 in
both arms, and each arm fired the RSP-source positive control. The real arm
produced 174 hangar image-stage rows (87 stage 2 and 87 stage 3) and 83 printed
consumer rows. Across the 257 observed callback events, adjacent cross-stream
events classified 46 image-after-consumer cases and 47 consumer-after-image
cases; 81 image events had no immediately adjacent consumer because multiple
image callbacks were grouped. Timestamps followed the same sequence order.

The silent arm reached the target phase and produced 21 consumer rows but no
image-stage rows, as expected from the intentional silent RSP arm. The retail
oracle was not run because its debugger-enabled core is unavailable.

This rejects a stable image-before-consumer scheduling boundary in the
measured real port arm. It does not refute `H-AudioDrainNotConsumed`: the
queue snapshots still differ, and this is single-source port evidence with no
retail callback parity. The next boundary is callback ownership/cadence, not a
single queue threshold or a stable callback order.

ORIGIN: diagnostic-only callback sequence/timestamp instrumentation. The
legitimate producer and consumer remain the existing `osAiSetNextBuffer` SDL
queue path and PCM callback; no mitigation or audio behavior change was added.
