# Cover the remaining pointer fields in the retail alternate source table
HYPOTHESIS-ID: m5-audio-destub

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

Exact preparation/run:

1. Build the oracle with `tools/oracle/build.sh`.
2. Run one 90-second capture with the same whole-RDRAM, target-span, source
   span, and `0x80007640` controls, plus the expanded pointer census; write to
   `scratch/agent/s4610_retail_pointer_targets.log`.
