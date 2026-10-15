# Next work unit

HYPOTHESIS-ID: m5-retail-port-reprepare-parity

Run one bounded retail/port reprepare parity join now that the independent
oracle reaches both selected mission origins. Capture publication/task identity
and route ordinal/row around `0x00690400` -> `0x00620400` on retail, while the
same-build port capture uses the existing phase-gated mission driver and route
diagnostics. Keep the whole-RDRAM, VI, and 512-wide hangar type-2 controls
positive. Do not add a mitigation.

Competing hypotheses and discriminator:

1. H-parity: retail and port both show a fresh publication/reprepare at the
   mission handoff, with matching route identity semantics.
2. H-publication-mismatch: retail reaches the handoff but lacks the port's
   fresh publication, or the two sides show materially different task/route
   identity behavior.
3. H-capture-invalid: any whole-RDRAM, VI, hangar-task, or mission-origin
   control fails, so no parity conclusion is selected.

The discriminating table is the first complete `0x00690400` -> `0x00620400`
window on each side: origin, task type/data, route ordinal, phase row, and
publication/reprepare event. A fresh transition on both sides selects
H-parity; a qualified mismatch selects H-publication-mismatch; a failed
control selects H-capture-invalid.

Build and run the port arm:

`cmake --build build --config Debug --target RogueSquadron64Recomp && zsh scratch/agent/s4923_mission_longevity.sh`

Run the retail arm with the validated oracle route and the existing whole-RDRAM
and task controls:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 240 --vi-poll --vi-trace --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,56:start,66:start,76:start,86:start,96:start,106:start,116:start,126:start,136:start,146:start,156:start,166:start --watch-write 0x0:0x800000 --pc-phase-log-width 0x6AB400:512 --watch-pc 0x80033FCC --pc-task-dump 0x80033FCC --pc-task-type 2`

Inspect only bounded summaries and origin/row joins from the two run logs.
Kill manual processes with SIGKILL; the scripts must self-watchdog.
