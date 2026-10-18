# Next work unit: M6 keyed mission endurance, segmented under the 600 s soak cap
HYPOTHESIS-ID: m6-mission-endurance

lldb is unusable (s5407). Start from scratch/agent/soak_queue/done/s5377_census_mission_retry_*.sh (rc=137 = hit 600 s cap):
trim to a <=540 s recipe that reaches mission origin 0x00690400, then holds, logging CRASH/abort and VI-origin stalls (>30 s unchanged).
Enqueue 3 segments (different key timing) and read SOAK-RESULTS.md. Each distinct failure: backtrace from the in-process
crash handler (main.cpp ~10078), name the writer, root-cause fix (mips64-elf-gcc PatchesLib patch allowed, two-arm qualification).
Outcomes: clean holds => extend segment length; CRASH/stall => capture and root-cause. Check CGSSessionScreenIsLocked first.
