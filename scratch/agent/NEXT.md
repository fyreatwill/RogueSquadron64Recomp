# NEXT work unit (s978)

Run one bounded external-oracle PIF read-watch arm using the freshly linked
oracle dylib whose only non-LTO object is `dbg_breakpoints.o`. Preserve a
whole-RDRAM write positive control, enable VI polling, and compare wrapper /
callback markers with exit status and VI count. Do not edit the recomp runtime.

HYPOTHESIS-ID: oracle-pif-callback-runtime

Competing hypotheses:

- H-pif-callback-artifact: the prior pre-start `rc=139` was caused by the
  all-LTO callback lowering; the corrected arm reaches callback return.
- H-pif-callback-path: the corrected ABI still crashes at callback entry or
  return, selecting a remaining debugger callback/path defect.
- H-pif-phase: the corrected arm survives, but retail remains at VI 320 and
  callback-table reachability is still phase-unevaluable.

Discriminating measurement: whole-RDRAM writes must fire; then compare the
PIF wrapper pre-callback, callback first-statement, and post-callback markers
with exit status and VI count. Return/completion selects H-pif-callback-artifact;
pre-return crash selects H-pif-callback-path; survival with VI 320 selects
H-pif-phase.

Exact command:

`env DYLD_LIBRARY_PATH=/Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build/Debug/rogue_squadron.z64 --secs 8 --watch-write 0x0:0x800000 --watch-read 0x1fc00000:0x1fc01000 --vi-poll --vi-trace`
