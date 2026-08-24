# NEXT work unit (s2301) — M5 target-phase construction-order join

HYPOTHESIS-ID: m5-step3-retail-task-output-writer

## Work unit

Ask the retail ground truth from the fixed s2300 capture first: whole-RDRAM,
title, hangar, and the width-512 target controls are positive; the target
bucket has `1,541` VI rows; and the three requested-PC class totals join their
writer histogram exactly (`1`, `1`, and `24`). Then make one bounded
oracle-only instrument change: retain every target-phase post-step sample for
`0x8008EB8C`, `0x8008EBBC`, and `0x80094648` in one ordinal sequence table with
`(ordinal,PC,VI,address,value,class)`. Preserve the existing class table,
filtered rows, lifetime sampler, writer histogram, watches, and controls.
Rebuild once and run one retail capture with the same eleven Start events. Do
not launch a port arm and do not implement a writer, writeback, consumer,
slot, gate, guard, or address remap.

## Competing hypotheses and discriminating measurement

- H-SharedSequence: EB8C and EBBC appear at the same VI/address/value tuple
  in adjacent sequence ordinals, while all 94648 sentinel events are outside
  that pair.
- H-DuplicatePublication: EB8C and EBBC publish the same tuple in separate
  non-adjacent events or at different VI/address/value tuples, without a
  94648 event interleaved between them.
- H-94648InterleavedHousekeeping: at least one 94648 sentinel event is
  ordinally between the EB8C and EBBC tuple events.
- H-CoverageInvalid: whole-RDRAM/title/hangar or target-bucket controls fail,
  or any requested-PC sequence count differs from its target writer count.

The discriminator is the complete, ordinally ordered target table joined to
the target writer histogram. Count every post-step sample, not only the first
or last tuple and not only non-sentinel rows. Make no contract change in any
case.

## Exact commands

1. Ground-truth checkpoint before rebuilding the instrument:

   `grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|pc-hist-phase|writer-pc-phase origin=0x006ab400 width=512 watch=2|post-target-class' scratch/agent/s2300_m5_target_value_class/oracle.log | tail -80`

2. In `tools/oracle/rs64_oracle.c`, add the bounded target sequence recorder
   at the existing delayed post-step requested-PC path. Use the pre-step
   latched `g_post_value_pending_vi`, `g_post_value_pending_width`, and
   `g_post_value_pending_origin`; record only width 512/origin `0x006AB400`,
   classify `0x7F7F7F7F` as sentinel, and append one row per requested-PC
   sample. Emit the complete bounded sequence at shutdown. Preserve the
   current class and legacy row output. Build with:

   `tools/oracle/build.sh`

3. Create
   `scratch/agent/run_s2301_m5_target_sequence_join.sh` from the s2300
   driver, changing only the output directory/name, sequence-table summary,
   and classification. Keep all watches, controls, Start presses, and the
   three `--post-value-pc` PCs.

4. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2301_m5_target_sequence_join.sh`

   `zsh scratch/agent/run_s2301_m5_target_sequence_join.sh`

The whole-RDRAM threshold, title, hangar, and positive width-512 target bucket
must all be present before interpreting sequence order. No runtime or
mitigation behavior is authorized by this measurement.
