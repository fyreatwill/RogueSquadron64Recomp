# Next work unit

HYPOTHESIS-ID: m5-audio-route-retail-mission-qualification

Run one bounded retail-only qualification capture to determine whether the
oracle can reach the mission handoff needed for the selected Factor5 route
reprepare parity test. Keep the existing port result as baseline and add no
mitigation.

Competing hypotheses and discriminator:

1. H-retail-mission-qualified: the oracle reaches one of the selected mission
   origins after the validated hangar route.
2. H-retail-route-absent: the oracle remains at title/hangar or another
   non-mission origin despite positive controls.
3. H-instrument-invalid: whole-RDRAM or VI controls fail; select no result.

The discriminator is the first post-hangar VI origin, not elapsed wall time.
Only H-retail-mission-qualified permits a later parity publication join.

Positive controls: whole-RDRAM watch must fire, VI polling must advance, and
the existing 512-wide hangar task witness must record type-2 rows.

Exact baseline/source commands:

`tools/oracle/build/rs64_oracle --core
/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
--rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
--secs 180 --vi-poll --vi-trace --video
/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
--press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,56:start,66:start,76:start,86:start,96:start,106:start,116:start,126:start,136:start,146:start,156:start,166:start
--watch-write 0x0:0x800000 --pc-phase-log-width 0x6AB400:512
--watch-pc 0x80033FCC --pc-task-dump 0x80033FCC --pc-task-type 2`
(whole-RDRAM control plus the existing hangar task/source witness). If the
oracle remains route-absent, record H-retail-route-absent and do not infer a
publication null.

`cmake --build build --config Debug --target RogueSquadron64Recomp && zsh scratch/agent/s4923_mission_longevity.sh`

Inspect only bounded source windows plus
`scratch/agent/s4923_mission_longevity/summary.txt` and bounded `grep -a`
matches from `run.log`; kill any manual process with SIGKILL.
