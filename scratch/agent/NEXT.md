# Next work unit (s4374): locate the title-specific decode/publication path

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4373 fixed oracle run passed controls and joined 1,959 valid type-2
tasks. C904/task joins were live in both title buckets and hangar, but the
five presumed intermediate PCs C950/C954/D78C/D790/DC38 executed only in
hangar. Do not repeat that five-PC table or the closed first-eight payload
comparison.

Competing hypotheses:

- H-title-alias: the title route uses an overlay-aliased or alternate PC
  range, so a range census around C904/DC38 will show title executions at
  different PCs.
- H-title-predecessor: title reaches the same transform through a caller or
  predecessor outside the presumed range; the range census stays empty while
  C904/task joins remain live.
- H-title-join-gap: the title execution watch is still under-armed or its
  phase gate is wrong; a positive-control and explicit title task/C904 rows
  remain live but the census has no usable title rows.

Discriminating measurement: one oracle build/run using a phase-gated execution
range census for `0x8009C904:0x8009DC3C`, joined to the latest typed task
ordinal, with explicit title and hangar phase buckets. Title PCs in the range
select H-title-alias; live title C904/task rows with no range hits select
H-title-predecessor; missing title task/C904 rows or a failed whole-RDRAM
control rejects the run as H-title-join-gap/instrument failure.

Exact commands:

    bash tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rsp /opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib --secs 75 --hit-cap 64 --watch-write 0x0:0x800000 --watch-pc 0x80033FCC --watch-pc-range 0x8009C904:0x8009DC3C --c904-witness --c904-task-join --pc-task-dump 0x80033FCC --pc-task-type 2 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x00790800:1024 --pc-phase-log-width 0x006AB400:512 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/soak_results/s4374_title_range.log 2>&1

Reject any run without 10,000 whole-RDRAM writes, all three phase buckets,
and at least 1,000 valid task joins.
