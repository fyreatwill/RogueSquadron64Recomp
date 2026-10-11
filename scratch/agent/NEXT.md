# RESUME: cover the remaining pointer fields in the retail alternate source table
HYPOTHESIS-ID: m5-audio-destub

This is the next discriminating work unit, not a rerun of s4609. The partial
result selected against the first eight visible pointers as the five-record
source, but did not resolve whether later pointers contain the records or
whether a different shared table supplies them.

The s4609 oracle run passed the whole-RDRAM control (12,155,017 callbacks),
reached VI-512 at VI 2269, saw 76 target-span writes, and fired the caller
watch 2,079 times. The first eight discovered pointers from `$a1=0x80165D9C`
contained code/control data and craft-name metadata, not the five copied name
records. The bounded cap stopped before later pointers such as `0x80154B20`,
so H-derived-records is still open.

Competing hypotheses:

- H-derived-records: the stable table base's pointer/metadata fields lead to the five records.
- H-other-shared-table: the base is staging metadata and the five records come from another RDRAM table or copy step.
- H-pointer-no-records: pointer fields are code/control structures and do not lead to the name records; the live source is elsewhere.

Discriminating measurement: capture 0x100 bytes at every aligned KSEG0 RDRAM
pointer in the 0x100-byte `0x165D9C` table, including the later fields missed by
the eight-target cap. A target containing the five records selects
H-derived-records; all targets lacking them selects H-pointer-no-records and
keeps H-other-shared-table open. The positive control, VI-512 phase,
execution-hit count, and target-span writes must all be present. Do not add a
mitigation.

Resume state: s4609's eight-target run is complete and must not be rerun. The
artifact is `scratch/agent/s4609_retail_pointer_targets.log`; its positive
control, VI-512 phase, caller execution control, and target-span control all
passed. No failed run or missing artifact needs recovery.

Exact preparation/run for the next iteration:

1. In `tools/oracle/rs64_oracle.c`, raise
   `MAX_PHASE_POINTER_TARGETS` from 8 to 64 with `apply_patch`; this is the
   required bounded-cap change before rebuilding.
2. Build the oracle with `tools/oracle/build.sh`.
3. Run one 90-second capture, preserving the same controls and using the
   expanded pointer census. Use:

   `tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 90 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1724c0:0x17250c --watch-write 0x165d9c:0x165e9c --watch-pc 0x80007640 --pc-phase-log 0x6ab400 --phase-pointer-watch 2:0x400 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s4610_retail_pointer_targets.log 2>&1`

   Confirm the positive control, VI-512 phase, execution-hit count, and
   target-span writes before interpreting pointer-target rows. A target with
   the five copied records selects H-derived-records; all expanded targets
   lacking them selects H-pointer-no-records and leaves H-other-shared-table.
   Do not add a mitigation.
