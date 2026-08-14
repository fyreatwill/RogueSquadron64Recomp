# NEXT work unit (s982)

Perform one bounded debugger callback-entry probe on the corrected external
oracle dylib. Do not edit the recomp runtime, add callback markers, or run a
retail soak.

HYPOTHESIS-ID: oracle-pif-callback-runtime

Competing hypotheses:

- H-pif-core-entry: the callback breakpoint is hit and the fault occurs in
  its first body instructions or diagnostic operation.
- H-pif-call-state: the callback breakpoint is hit and the fault occurs only
  after a state-dependent load/call, identifying emulator/core state as the
  remaining boundary.
- H-pif-pre-entry: the wrapper's direct branch does not reach `0x1b80`, or
  the debugger shows a fault before callback entry despite the static target.

Discriminating measurement: one debugger run must capture whether `0x1b80` is
hit, the register values at entry, and the exact faulting instruction. Entry
plus a fault in the prologue/diagnostic path selects H-pif-core-entry; entry
plus a later state-dependent fault selects H-pif-call-state; no entry selects
H-pif-pre-entry.

Exact command:

`lldb -- /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build/Debug/rogue_squadron.z64 --secs 8 --watch-write 0x0:0x800000 --watch-read 0x1fc00000:0x1fc01000 --vi-poll --vi-trace`

At the debugger prompt: `br s -n check_breakpoints_on_mem_access`, `run`,
then on stop `register read x0 x1 x2 x3 pc sp` and `continue`; capture the
faulting instruction/backtrace if it stops again. The existing source and
binary audits are the baseline. No retail phase result may be inferred.
