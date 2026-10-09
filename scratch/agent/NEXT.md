# Next work unit (s4376): join title caller to task publication

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4375 qualified retail census found title-phase execution in
`0x80019C00:0x80019E20`, including the observed chain
`0x80019DEC -> 0x80033FCC`; the typed task join was live. Do not repeat the
broad caller range or the closed first-eight payload comparison.

Competing hypotheses:

- H-publish-direct: the title caller at `0x80019DEC` passes the same task
  identity/arguments directly into `0x80033FCC`; phase-keyed rows will show
  matching caller `$a0` and task pointer/ordinal adjacency.
- H-publish-transform: the caller is only a pre-publication stage; title rows
  at `0x80019DEC` are live but its arguments differ from the task publication
  fields or are separated by another call.
- H-title-watch-gap: the prior range result was an attribution artifact; the
  explicit `0x80019DEC` watch will have no title rows despite live title
  C904/task rows.

Discriminating measurement: one retail oracle run with explicit watches at
`0x80019DEC` and `0x80033FCC`, phase-gated title/hangar GPR rows, the typed
task dump, C904/task join, whole-RDRAM positive control, and all three VI
buckets. Title caller rows adjacent to matching `0x80033FCC` task pointers
select H-publish-direct; live title caller rows with changed/separated task
fields select H-publish-transform; missing title caller rows or any failed
control rejects the result as H-title-watch-gap/instrument failure.

Exact commands:

    bash tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rsp /opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib --secs 75 --hit-cap 64 --watch-write 0x0:0x800000 --watch-pc 0x80019DEC --watch-pc 0x80033FCC --c904-witness --c904-task-join --pc-task-dump 0x80033FCC --pc-task-type 2 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x00790800:1024 --pc-phase-log-width 0x006AB400:512 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/soak_results/s4376_title_publish.log 2>&1

Reject any run without 10,000 whole-RDRAM writes, all three phase buckets,
and at least 1,000 valid type-2 task joins.
