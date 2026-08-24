# NEXT work unit (s2294) — M5 target-phase slot writer-PC histogram

HYPOTHESIS-ID: m5-step3-retail-port-writer-join

## Work unit

Run one oracle-only retail capture retaining the independent whole-RDRAM,
task/output, title, hangar, watched-PC, post-value, and exact 16-slot controls
from s2293. Add `--pc-hist-phase 0x006AB400` for every slot watch. The new
table must classify the writer PCs that actually touch each slot during the
hangar target phase, not just lifetime writer totals. Do not launch a port arm
and do not implement a writer, writeback, consumer, slot, gate, guard, or
address remap.

## Competing hypotheses and discriminating measurement

- H-AllCandidateWritesPreTarget: every slot's target-phase writer histogram is
  empty while its lifetime count remains `768`; the retail slot writes all
  occur before the hangar target phase.
- H-TargetWriter078EC: one or more target-phase slot histograms contain
  `0x800078EC`; the watched PC is a direct target-phase candidate-slot writer,
  even though s2293's post-target table was empty.
- H-TargetWriterOther: one or more target-phase slot histograms are nonzero,
  but contain only a PC other than `0x800078EC`; the current watched PC is not
  the target-phase slot writer.
- H-CoverageInvalid: the whole-RDRAM threshold, title, or hangar control is
  absent; no target-phase writer null is interpretable.

The discriminator is one 16-row table keyed by `(slot, lifetime writes,
target-phase writes, target-phase writer-PC histogram, post-value samples,
final nonzero/FNV)`. Controls plus all-zero target-phase buckets select
H-AllCandidateWritesPreTarget; a target bucket containing `0x800078EC`
selects H-TargetWriter078EC; a nonzero bucket with another PC selects
H-TargetWriterOther; missing controls select H-CoverageInvalid.

## Exact commands

1. Create the self-contained driver
   `scratch/agent/run_s2294_m5_target_slot_writer_phase.sh`. It must use the
   same oracle/core/ROM/Rice paths and eleven named Start presses as s2293,
   with watch indexes 0=`0x0:0x800000`, 1=`0x166000:0x16A000`,
   2=`0x141AD0:0x141AF0`, and 3–18 the 16 `0x300` windows beginning at
   `0x166450` through `0x169150`. Arm `--watch-pc 0x800078EC`,
   `--pc-phase-log-width 0x006AB400:512`, `--pc-hist-phase 0x006AB400`,
   `--pc-hist-watch 3` through `18`, `--post-value-pc 0x800078EC`, and
   `--post-value-watch 3` through `18`; retain `--vi-trace`, `--hit-cap 200`,
   and the natural 120-second oracle shutdown.
2. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2294_m5_target_slot_writer_phase.sh`

   `zsh scratch/agent/run_s2294_m5_target_slot_writer_phase.sh`

If any independent control is absent, record H-CoverageInvalid and do not
interpret target-phase writer or post-value nulls.
