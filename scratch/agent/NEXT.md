# NEXT work unit (s960)

Run one bounded 30-second retail-oracle arm with a direct physical PIF-range
read watch and `--press 6:start`, `--verbose`, and `--vi-poll`. s959 confirmed
input-plugin attachment and press delivery, but its PIF trace is only a per-VI
poll and cannot attribute a game-side PIF read. No build or generated-code edit
is needed.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-oracle-game-no-pif-read: the retail game never reaches a CPU read of PIF
  RAM while it remains at VI 320.
- H-oracle-pif-address: the game reads controller state through a different
  physical range than `0x1FC007C0..0x1FC007C8`.
- H-oracle-read-watch: the game reads the documented PIF range, but the oracle
  debugger's read breakpoint path does not report it.

Discriminating measurement: whole-RDRAM writes plus a direct physical read watch
on `0x1FC007C0:0x1FC007C8` in the same driven run. PIF-range hits select game
read activity; zero PIF hits with a passing control selects no-read or wrong
address, while an independently confirmed read with no breakpoint hit selects
the oracle read-watch path. The whole-RDRAM positive control must visibly fire.

Exact starting commands (create the result directory first):

`mkdir -p scratch/agent/oracle_results/s959_oracle_phase`

`rg -n "PIF_PAD1_ADDR|watch-read|DebugMemRead32|Input-SDL-Control1|Start|attach_plugin" tools/oracle /Users/williambuckley/Documents/Tools/rs64-oracle/src /Users/williambuckley/Documents/Tools/rs64-oracle/cfg`

`mkdir -p scratch/agent/oracle_results/s960_pif_read && tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 30 --watch-write 0x0:0x800000 --watch-read 0x1FC007C0:0x1FC007C8 --hit-cap 200 --vi-poll --verbose --press 6:start > scratch/agent/oracle_results/s960_pif_read/driven.log 2>&1`
