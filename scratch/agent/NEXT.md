# Snapshot the retail alternate source table
HYPOTHESIS-ID: m5-audio-destub

The s4607 oracle run passed the whole-RDRAM control (10,076 callbacks), reached
the VI-512 hangar gate, and saw 76 target-span writes. The phase-gated execution
watch at `0x80007640` fired 2,079 times; the relevant caller `0x80022B44`
repeatedly passed `$a1=0x80165D9C` (105 bounded rows), an RDRAM pointer. This
selects the alternate shared source-table hypothesis.

Competing hypotheses:

- H-table-layout: the five target records are sourced from a contiguous or
  strided table around physical `0x165D9C`.
- H-derived-records: `$a1=0x80165D9C` is a stable table base, but callers derive
  each record through nearby pointers/offsets before the writer.
- H-other-shared-table: the observed pointer is a common staging table and the
  five records come from another RDRAM table or copy step.

Discriminating measurement: add a bounded phase-gated memory snapshot around
physical `0x165D9C` (at least 0x100 bytes) and retain the `$a1`, `$a0`, and
`prev_pc` rows at `0x80007640`, while keeping the whole-RDRAM positive control
and target-span writer watch in the same run. A stable five-record pattern at
the shared base selects H-table-layout; changing nearby source bases/offsets
joined to the five target writes selects H-derived-records; an unchanged table
with records appearing from a separate watched source selects H-other-shared-table.
The positive control, phase-arm line, execution-hit count, and target-write count
must all be present.

Exact preparation/run:

1. Extend the oracle's existing phase-gated source snapshot/row output for
   `0x80165D9C`, then rebuild with `tools/oracle/build.sh`.
2. Run the same s4607 command, adding the source snapshot option, and write to
   `scratch/agent/s4608_retail_source_table.log`:

   `tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 90 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1724C0:0x17250C --watch-pc 0x80007640 --pc-phase-log-width 0x006AB400:512 --pc-phase-quiet --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s4608_retail_source_table.log 2>&1`

No mitigation.
