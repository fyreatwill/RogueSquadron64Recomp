# NEXT work unit (s2299) — M5 non-sentinel target writer sequence join

HYPOTHESIS-ID: m5-step3-retail-task-output-writer

## Work unit

Ask the retail ground truth from the completed s2298 capture first: its
whole-RDRAM, title, hangar, and width-512 controls are positive, the target
bucket has `1,515` VI rows, and target writer `0x80094648` has `24` hits, but
the 16-row table is filled by `0x7F7F7F7F` sentinels while EB8C and EBBC have
no target hits. Then make one bounded oracle-only instrument change: in the
pre-step-latched requested-row recorder, filter the known sentinel value
`0x7F7F7F7F` before consuming the per-PC 16-row cap. Keep the existing
requested-PC list, phase latch, watches, and controls. Rebuild once and run
one retail capture with the same eleven Start events. Do not launch a port arm
and do not implement a writer, writeback, consumer, slot, gate, guard, or
address remap.

## Competing hypotheses and discriminating measurement

- H-94648Distinct: filtered rows show unique non-sentinel target tuples from
  `0x80094648`, while EB8C and EBBC remain absent or metadata-only.
- H-EB8COrEBBCHousekeeping: exactly one of EB8C/EBBC yields a non-sentinel
  target publication and `0x80094648` remains sentinel-only.
- H-SharedConstruction: all three requested PCs yield overlapping ordered
  non-sentinel target tuples after sentinel rows stop consuming the cap.
- H-TargetRowsInsufficient: controls fail, or the filtered target row table is
  still empty/capped, so no role conclusion is allowed.

The discriminator is one table keyed by `(writer PC, pre-store VI/origin,
address, post-step value, sentinel class, ordinal)` from the retained
`post-target-row-final` records, joined with the target-phase writer counts.
Select H-94648Distinct when 94648 has unique non-sentinel tuples and neither
EB8C nor EBBC supplies the same construction; select H-EB8COrEBBCHousekeeping
only when exactly one of EB8C/EBBC publishes and 94648 is sentinel-only;
select H-SharedConstruction only when all three overlap in one ordered
sequence. If the independent controls fail, select H-CoverageInvalid; if the
filtered target table remains empty or capped, select H-TargetRowsInsufficient.
Make no contract change in either case.

## Exact commands

1. Ground-truth checkpoint before rebuilding the instrument:

   `grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|pc-hist-phase|writer-pc-phase origin=0x006ab400 width=512 watch=2' scratch/agent/s2298_m5_pre_step_phase_writer_sequence/oracle.log | tail -40`

2. In `tools/oracle/rs64_oracle.c`, make the pre-step-latched
   `record_post_value_requested_row()` ignore value `0x7F7F7F7F` before
   consuming the per-PC 16-row cap. Preserve the requested-PC list, phase
   latch, and all other post-value statistics. Build with:

   `tools/oracle/build.sh`

3. Create
   `scratch/agent/run_s2299_m5_non_sentinel_target_writer_sequence.sh` from
   the s2298 driver, changing only the output directory/name and summary
   labels. Keep all watches, controls, Start presses, and the three
   `--post-value-pc` PCs. Print at most 16 filtered target rows per PC and
   classify the four hypotheses above.

4. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2299_m5_non_sentinel_target_writer_sequence.sh`

   `zsh scratch/agent/run_s2299_m5_non_sentinel_target_writer_sequence.sh`

The whole-RDRAM threshold, title, hangar, and positive width-512 target bucket
must all be present before interpreting any writer row. No runtime or
mitigation behavior is authorized by this measurement.
