# NEXT work unit (s2300) — M5 target-phase writer value-class join

HYPOTHESIS-ID: m5-step3-retail-task-output-writer

## Work unit

Ask the retail ground truth from the completed s2299 capture first: its
whole-RDRAM, title, hangar, and width-512 controls are positive, the target
bucket has `942` VI rows, target writer `0x80094648` has `24` hits, and the
pre-step-latched filtered row table retained no rows for any requested PC.
Then make one bounded oracle-only instrument change: add a target-phase
post-step value-class table for `0x8008EB8C`, `0x8008EBBC`, and `0x80094648`
that counts sentinel and non-sentinel values and retains the first and last
`(VI,address,value)` tuple per class. Preserve the existing requested-PC
list, phase latch, generic lifetime sampler, watches, and controls. Rebuild
once and run one retail capture with the same eleven Start events. Do not
launch a port arm and do not implement a writer, writeback, consumer, slot,
gate, guard, or address remap.

## Competing hypotheses and discriminating measurement

- H-94648SentinelOnly: target-phase post-step samples at `0x80094648` are all
  `0x7F7F7F7F`, while EB8C and EBBC have no target samples.
- H-94648TargetPublication: `0x80094648` has at least one non-sentinel target
  value and neither EB8C nor EBBC has a target value.
- H-OtherOrSharedConstruction: EB8C or EBBC has a target value; the complete
  first/last tuple table distinguishes one-PC housekeeping from overlapping
  construction.
- H-CoverageInvalid: whole-RDRAM/title/hangar or target-bucket controls fail,
  or target writer hits have no corresponding post-step value-class samples.

The discriminator is one table keyed by `(writer PC, pre-store VI/origin,
address, post-step value, sentinel class, ordinal)` from every target-phase
post-step sample, joined with the target-phase writer counts. The sample count
must account for all `0x80094648` target hits; otherwise select
H-CoverageInvalid. Make no contract change in either case.

## Exact commands

1. Ground-truth checkpoint before rebuilding the instrument:

   `grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|pc-hist-phase|writer-pc-phase origin=0x006ab400 width=512 watch=2|post-target-rows' scratch/agent/s2299_m5_non_sentinel_target_writer_sequence/oracle.log | tail -60`

2. In `tools/oracle/rs64_oracle.c`, extend the pre-step-latched requested-PC
   recorder with the complete target value-class table described above. Emit
   one bounded summary per requested PC and class at shutdown. Preserve the
   sentinel filter, requested-PC list, phase latch, generic lifetime sampler,
   and all existing controls. Build with:

   `tools/oracle/build.sh`

3. Create
   `scratch/agent/run_s2300_m5_target_value_class.sh` from the s2299 driver,
   changing only the output directory/name and summary labels. Keep all
   watches, controls, Start presses, and the three `--post-value-pc` PCs.
   Print the complete bounded value-class table and classify the four
   hypotheses above.

4. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2300_m5_target_value_class.sh`

   `zsh scratch/agent/run_s2300_m5_target_value_class.sh`

The whole-RDRAM threshold, title, hangar, and positive width-512 target bucket
must all be present before interpreting any writer row. No runtime or
mitigation behavior is authorized by this measurement.
