# NEXT work unit (s979)

Classify the corrected oracle callback crash boundary with one static/runtime
audit. Use the already validated `iter974-armB2` dylib and inspect the exact
`read_with_bp_checks` call, callback symbol binding, callback prologue, and
first diagnostic body; then run one 3-second PIF-watch arm under the same
positive-control setup. Do not edit the recomp runtime.

HYPOTHESIS-ID: oracle-pif-callback-runtime

Competing hypotheses:

- H-pif-direct-target: the corrected caller's direct branch resolves to an
  invalid or incompatible callback address at runtime.
- H-pif-prologue: the callback target is correct, but entry/prologue state
  (stack, ABI, or symbol body) faults before the first marker.
- H-pif-marker-body: callback entry succeeds and the first diagnostic body
  faults before its marker, so the marker placement is misleading.

Discriminating measurement: `nm`/`otool` must identify the direct branch target
and callback entry/prologue, while the positive-control PIF run must compare
wrapper pre-callback, callback first-statement, and post-callback markers. A
bad/unresolved target selects H-pif-direct-target; a valid target with no first
marker selects H-pif-prologue; a first marker followed by no return selects
H-pif-marker-body.

Exact commands:

`nm -n /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib | rg 'read_with_bp_checks|check_breakpoints_on_mem_access'`

`otool -tvV /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib | sed -n '1,1155p' | rg 'read_with_bp_checks|check_breakpoints|mov w[0-3]|bl\s'`

`env DYLD_LIBRARY_PATH=/Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/rogue_squadron.z64 --secs 3 --watch-write 0x0:0x800000 --watch-read 0x1fc00000:0x1fc01000 --vi-poll --vi-trace`
