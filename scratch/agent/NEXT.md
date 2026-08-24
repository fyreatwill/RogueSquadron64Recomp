# NEXT work unit (s2297) — M5 target-only writer sequence join

HYPOTHESIS-ID: m5-step3-retail-task-output-writer

## Work unit

Ask the retail ground truth already captured in
`scratch/agent/s2296_m5_target_output_writer_pc_join/oracle.log` first: its
whole-RDRAM, title, hangar, and width-512 controls are positive, and its
`0x80094648` post-target table is saturated by title sentinel rows before the
target phase. Then make one bounded oracle-instrument change so requested
post-value rows are retained only when `width=512` and
`origin=0x006AB400`; rebuild the oracle and run one retail capture with the
s2296 controls. This keeps the existing 16-row per-PC cap while ensuring it
captures target rows rather than title sentinels. Do not launch a port arm and
do not implement a writer, writeback, consumer, slot, gate, guard, or address
remap.

## Competing hypotheses and discriminating measurement

- H-SharedConstruction: all three PCs contribute to one target-phase
  construction sequence, with matching or ordered overlapping
  `(address,value)` tuples.
- H-94648Distinct: `0x80094648` contributes unique non-sentinel target
  address/value tuples, while `0x8008EB8C` and `0x8008EBBC` remain the same
  metadata publication step.
- H-EB8COrEBBCHousekeeping: one of the two `0x141AD0` writers is a duplicate
  or housekeeping store and the other is the only non-sentinel publisher;
  `0x80094648` contributes only sentinel target writes.
- H-TargetRowsInsufficient: the target-only table still cannot capture a
  complete ordered join, so no role conclusion is allowed.

The discriminator is one table keyed by `(writer PC, target VI/origin,
address, value, sentinel class, ordinal)` from the target-only
`post-target-row-final` records, joined with the target-phase writer counts.
Select H-SharedConstruction when the three PCs overlap in one ordered
sequence; select H-94648Distinct when 94648 has unique non-sentinel tuples;
select H-EB8COrEBBCHousekeeping only when exactly one of EB8C/EBBC has the
non-sentinel publication and 94648 is sentinel-only. If the independent
controls or target-only row capacity fail, select H-CoverageInvalid or
H-TargetRowsInsufficient and make no contract change.

## Exact commands

1. Ground-truth checkpoint before rebuilding the instrument:

   `grep -a -E 'positive-control threshold|origin=0x006ab400 width=512|post-target-row-final pc=0x80094648|writer-pc-phase origin=0x006ab400' scratch/agent/s2296_m5_target_output_writer_pc_join/oracle.log | tail -40`

2. Add the target-only condition in
   `tools/oracle/rs64_oracle.c` inside
   `record_post_value_requested_row()`: return without recording unless the
   live VI width is `512` and origin is `0x006AB400`. Preserve the existing
   requested-PC list and 16-row cap. Build with:

   `tools/oracle/build.sh`

3. Create
   `scratch/agent/run_s2297_m5_target_only_writer_sequence.sh` from the
   s2296 driver, changing only the output directory/name and keeping all
   watches, controls, Start presses, and three `--post-value-pc` PCs. Update
   its summary/verdict to count only target-origin non-sentinel rows and to
   print at most 16 rows per PC.

4. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2297_m5_target_only_writer_sequence.sh`

   `zsh scratch/agent/run_s2297_m5_target_only_writer_sequence.sh`

The whole-RDRAM threshold, title, hangar, and positive width-512 target bucket
must all be present before interpreting any writer row. No runtime or
mitigation behavior is authorized by this measurement.
