# Next work unit (s4317): capture a complete hangar-gated retail consumer stream

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4316): the retail route is qualified with Rice video, eleven documented
Start presses, the whole-RDRAM control, and the 1024->512 transition at 38.4 s
to origin `0x006AB400`. The first comparison had only 14,140 filtered consumer
rows; the detail-gated retry stalled before VI 512. The port side remains
qualified at 16,384 rows.

Competing hypotheses:

- H-port: the port's first 16,384 keyed rows are not stable under the current seeded route.
- H-layout: retail and port diverge in the consumer stream's layout/order.
- H-filter: retail detail rows include unrelated target-block traversal.

Discriminator: run the oracle with `RS64_DETAIL_HANGAR_READ=1` and the proven
s4315 route. Require the whole-RDRAM positive control, VI-512 transition at
`0x006AB400`, and exactly 16,384 hangar-gated rows; then compare ordinal
`(PC,address,value)` against the qualified port table. A first mismatch on a
consumer PC selects H-layout, non-consumer rows select H-filter, and a full
match selects H-port. Any missing control, transition, or row count invalidates
the arm. No guard/skip is authorised.

Exact command (kill with SIGKILL only):

`env RS64_DETAIL_HANGAR_READ=1 tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 120 --hit-cap 200 --watch-write 0x0:0x800000 --watch-read 0x17D000:0x17E200 --detail-watch 1 --watch-pc 0x8008FCE8:0x8008FCEC --detail-watch 2 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s4317_oracle.log 2>&1`

Use `scratch/agent/s4316_compare_streams.py` after extracting the 16,384
hangar-gated rows; do not add another diagnostic field or mitigation.
