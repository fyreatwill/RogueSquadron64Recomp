# NEXT work unit — M5 phase-matched selector-table writer boundary

HYPOTHESIS-ID: m5-selector-writer-input-boundary

Session 3510 was unevaluable because retail stores occurred at hangar origin
`0x006AB400` while the port witness captured title origin `0x00790400`.
Extend the existing port table-store phase predicate to capture both origins,
then compare the hangar rows to retail in one bounded run.

Competing hypotheses and discriminating measurement:

- `H-InputParity`: writer register/input context and selector index match
  across runtimes; the difference is an earlier table initializer value.
- `H-InputDivergence`: the first writer input or index differs, selecting the
  upstream producer/selection edge.
- `H-PortWriterRoute`: the port reaches the stores through a materially
  different caller/route despite matching writer PCs.
- `H-CaptureInvalid`: either independent retail whole-RDRAM/title controls or
  the port title/schema controls fail; the join is unevaluable.

Discriminating measurement: one batched retail/port capture that keeps the
whole-RDRAM control, corrected table-store watch, existing selector pre-call
and load controls, and the store-register context. Join by shared origin,
table address, writer PC, stored value, writer arguments/registers, and
selector index. Matching inputs with differing values selects an initializer;
a first differing input/index selects its producer; missing controls make the
join unevaluable.

Before building, run the independent retail oracle first with whole-RDRAM
control, corrected table span, and the `0x006AB400`/1024 phase bucket. Build
and run the validated real-image/LLE/spin-yield/autopilot route with both title
and hangar store buckets. Do not repeat the unchanged title-only store census.

Exact ground-truth command before the port build:
`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 40 --hit-cap 1000 --watch-write 0x0:0x800000 --watch-write 0x149758:0x149760 --watch-pc 0x8008F228,0x8008F264 --pc-phase-log-width 0x790400:1024 --pc-field-dump 0x8008F228,0x8008F264 --store-field-dump 1:0x80149758,0x8014975C --post-value-watch 1 --pc-hist-watch 1 --pc-hist-phase 0x790400:1024 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start --hold-ms 150 > scratch/agent/s3510_selector_retail.log 2>&1`

Expected split: positive whole-RDRAM/title controls plus matching writer
inputs and differing stores selects an initializer/value edge; a first
input/index difference selects the upstream producer; a route-only mismatch
selects dispatch divergence; any missing control makes the join unevaluable.
