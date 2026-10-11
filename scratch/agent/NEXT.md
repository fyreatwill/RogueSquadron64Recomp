# RESUME: identify the retail source path after pointer-target exclusion
HYPOTHESIS-ID: m5-audio-destub

This is the next single work unit. s4611 expanded the retail pointer census
to 17 targets and found no five copied name records or `late`. The run passed
whole-RDRAM, VI-512, pointer-source, and target-span controls, but the
`0x80007640` execution watch was 0, so the pointer result is explicitly
single-source/caveated. Do not promote a stronger null until the caller
control is live.

Competing hypotheses:

- H-other-shared-table: the five target records come from another retail RDRAM
  source/table; visible pointer targets remain metadata/control only.
- H-pointer-no-records: the visible pointers are not record sources and the
  caller uses a stable alternate operand/source outside those targets.
- H-control-invalid: the source/target observations are phase-valid, but the
  absent `0x80007640` execution hit means the caller attribution is not
  qualified and the source path remains unevaluable.

Discriminating measurement: add one phase-scoped source-origin table to the
oracle, retaining the expanded 17 pointer snapshots, that records (a) writes
to `0x165D9C..0x165E9C`, (b) writes to every discovered pointer target, (c) the
five target-record writes, and (d) a live caller-PC control (use the actual
retail writer PC if the existing `0x80007640` range remains zero). A distinct
source/write operand with no visible-target writes selects H-other-shared-table;
a stable alternate operand with no visible-target records selects
H-pointer-no-records; a zero caller control leaves H-control-invalid and
requires fixing the control before interpreting nulls. Whole-RDRAM, VI-512,
pointer-source, and target-span controls must all fire in the same run. Do not
add a mitigation.

Preparation and run:

1. Update the oracle instrumentation in `tools/oracle/rs64_oracle.c` and its
   help text in the same change; keep the 64-target cap.
2. Build with `tools/oracle/build.sh`.
3. Run one Rice-qualified 90-second capture from the repo root, preserving:

   `tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 90 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1724c0:0x17250c --watch-write 0x165d9c:0x165e9c --watch-pc 0x80007640 --pc-phase-log 0x6ab400 --phase-pointer-watch 2:0x400 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s4612_retail_source_origin.log 2>&1`

Check all controls before interpreting the source rows. Do not add a
mitigation.
