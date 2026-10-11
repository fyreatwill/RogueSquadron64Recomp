# Capture the retail source operand at rs_strncpy
HYPOTHESIS-ID: m5-audio-destub

The s4606 oracle run passed the whole-RDRAM control (21,009 hits), reached the
VI-512 hangar gate, and captured the candidate span
`0x62B9F8..0x62BA98` as all `0xFF` despite 10,933 lifetime writes. The target
span received 76 writes, all from `0x80007670`. The candidate source location
is therefore not retail's live input, but the alternate input is not located.

Competing hypotheses:

- H-alt-source-table: retail `rs_strncpy` receives the five records from one
  other shared RDRAM table or copied buffer.
- H-direct-callsite: retail call sites provide five distinct literal or
  derived source operands to the same writer.
- H-host-translation: the source operand is non-RDRAM or unstable because a
  host-side path supplies the bytes before the guest writer.

Discriminating measurement: extend the oracle's watched-execution output to
include `$a1` at guest `rs_strncpy` entry `0x80007640`, phase-gated to
`0x006AB400:512`, then run one capture with the existing whole-RDRAM positive
control and target-span writer watch. A repeated/shared alternate `$a1` in
RDRAM selects H-alt-source-table; five distinct literal/derived `$a1` values
select H-direct-callsite; non-RDRAM or unstable values keep
H-host-translation open. The result must include an execution-hit control and
the target writer control before any null is interpreted.

Exact preparation/run:

1. Add a bounded `$a1` field to the oracle's existing `--watch-pc` row for
   `0x80007640`; rebuild with `tools/oracle/build.sh`.
2. Run from the repo root:

   `tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 90 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1724C0:0x17250C --watch-pc 0x80007640 --pc-phase-log-width 0x006AB400:512 --pc-phase-quiet --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s4607_retail_source_operand.log 2>&1`

No mitigation.
