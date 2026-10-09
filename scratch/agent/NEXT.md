# Next work unit (s4375): census the title caller chain

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4374 qualified oracle run passed controls and joined 3,361,701 C904/task
rows with 1,571 valid type-2 tasks. The range `0x8009C904:0x8009DC3C` had
16,264,908 execution hits and joined rows only in hangar, while title C904/task
witnesses remained live. Do not repeat that range, the five-PC table, or the
closed first-eight payload comparison.

Competing hypotheses:

- H-title-caller: the title path's caller chain is in `0x80019C00:0x80019E20`,
  so the range will produce title-phase rows joined to typed tasks.
- H-title-predecessor-deeper: title reaches the same transform through an
  earlier or alternate caller; the caller census stays empty while title
  C904/task joins remain live.
- H-title-join-gap: the title execution watch is still under-armed or its
  phase gate is wrong; the positive control or explicit title task/C904 rows
  fail despite the range being armed.

Discriminating measurement: one oracle build/run using a phase-gated execution
range census for `0x80019C00:0x80019E20`, joined to the latest typed task ordinal,
with explicit title and hangar phase buckets. Title range rows joined to typed
tasks select H-title-caller; live title C904/task rows with no caller-range
rows select H-title-predecessor-deeper; missing title task/C904 rows or a
failed whole-RDRAM control rejects the run as H-title-join-gap/instrument
failure.

Exact commands:

    bash tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rsp /opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib --secs 75 --hit-cap 64 --watch-write 0x0:0x800000 --watch-pc 0x80033FCC --watch-pc-range 0x80019C00:0x80019E20 --c904-witness --c904-task-join --pc-task-dump 0x80033FCC --pc-task-type 2 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x00790800:1024 --pc-phase-log-width 0x006AB400:512 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/soak_results/s4375_title_caller.log 2>&1

Reject any run without 10,000 whole-RDRAM writes, all three phase buckets,
and at least 1,000 valid task joins.
