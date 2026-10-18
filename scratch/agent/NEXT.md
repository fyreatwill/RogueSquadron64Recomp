# Next work unit: M6 keyed mission holds
HYPOTHESIS-ID: m6-mission-endurance
Autopilot route stops in the hangar (s5391 r1: 880 s clean hangar hold). Find the s5378 recipe (grep loop.log / soak_results for s5378; it reached 0x00690400), extend scratch/agent/m6_hold.sh with the hangar->mission key step (winctl key, needs unlocked screen), then run >=3 holds of >=10 min. Each distinct crash/stall: lldb backtrace, name the writer, root-cause fix (mips64-elf-gcc available for PatchesLib C patches). Outcomes: all clean = endurance datum; crash = backtrace.
