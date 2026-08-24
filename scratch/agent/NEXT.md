# NEXT work unit (s2298) — M5 pre-step-phase writer sequence join

HYPOTHESIS-ID: m5-step3-retail-task-output-writer

## Work unit

Ask the retail ground truth from the completed s2297 capture first: its
whole-RDRAM, title, hangar, and width-512 controls are positive, the target
bucket has `925` VI rows, but its task/output target-phase writer histogram and
all three target-only row tables are empty. Then make one bounded oracle-only
instrument change: latch the live `(g_vis, VI width, VI origin)` at the
pre-store memory-breakpoint callback and carry that metadata into the existing
post-step value row. Keep the existing requested-PC list and 16-row cap, and
retain rows only when the latched phase is `width=512, origin=0x006AB400`.
Rebuild once and run one retail capture with the s2297 watches, eleven Start
events, and controls. Do not launch a port arm and do not implement a writer,
writeback, consumer, slot, gate, guard, or address remap.

## Competing hypotheses and discriminating measurement

- H-SharedConstruction: the pre-step-phase paired rows from all three PCs
  overlap in one ordered target construction sequence.
- H-94648Distinct: `0x80094648` contributes unique non-sentinel target
  address/value tuples while EB8C and EBBC remain the same metadata step.
- H-EB8COrEBBCHousekeeping: exactly one of EB8C/EBBC has the non-sentinel
  publication and `0x80094648` is target-sentinel-only.
- H-TargetRowsInsufficient: the target-phase writer or paired row table is
  still empty or capped, so no role conclusion is allowed.

The discriminator is one table keyed by `(writer PC, pre-store VI/origin,
address, post-step value, sentinel class, ordinal)` from the retained
`post-target-row-final` records, joined with the target-phase writer counts.
Select H-SharedConstruction when all three PCs overlap in one ordered
sequence; H-94648Distinct when 94648 has unique non-sentinel tuples;
H-EB8COrEBBCHousekeeping only when exactly one of EB8C/EBBC publishes and
94648 is sentinel-only. If the independent controls fail, select
H-CoverageInvalid; if the target writer/row capacity still fails, select
H-TargetRowsInsufficient. Make no contract change in either case.

## Exact commands

1. Ground-truth checkpoint before rebuilding the instrument:

   `grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|pc-hist-phase|writer-pc-phase origin=0x006ab400 width=512 watch=2' scratch/agent/s2297_m5_target_only_writer_sequence/oracle.log | tail -40`

2. In `tools/oracle/rs64_oracle.c`, add pending pre-step phase fields for the
   requested post-value sample. Set them in the write-breakpoint path before
   `pDebugStep()`, pass them to `record_post_value_requested_row()`, and make
   that function filter on the latched fields rather than reading the live VI
   registers after the step. Preserve the existing requested-PC list and
   16-row cap. Build with:

   `tools/oracle/build.sh`

3. Create
   `scratch/agent/run_s2298_m5_pre_step_phase_writer_sequence.sh` from the
   s2297 driver, changing only the output directory/name and summary labels.
   Keep all watches, controls, Start presses, and the three `--post-value-pc`
   PCs. Print at most 16 latched target rows per PC and classify the four
   hypotheses above.

4. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2298_m5_pre_step_phase_writer_sequence.sh`

   `zsh scratch/agent/run_s2298_m5_pre_step_phase_writer_sequence.sh`

The whole-RDRAM threshold, title, hangar, and positive width-512 target bucket
must all be present before interpreting any writer row. No runtime or
mitigation behavior is authorized by this measurement.
