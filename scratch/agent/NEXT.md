# NEXT work unit (s2295) — M5 target-phase task/output writer-PC histogram

HYPOTHESIS-ID: m5-step3-retail-task-output-writer

## Work unit

Run one oracle-only retail capture retaining the independent whole-RDRAM,
title, hangar, watched-PC, candidate-span, and exact 16-slot controls from
s2294. Add lifetime and target-phase writer-PC histograms plus post-value
sampling for watch 2, the independent task/output span
`0x141AD0:0x141AF0`. Use the width-aware `--pc-hist-phase
0x006AB400:512` bucket. Do not launch a port arm and do not implement a
writer, writeback, consumer, slot, gate, guard, or address remap.

## Competing hypotheses and discriminating measurement

- H-TaskOutputPreTarget: watch 2 has lifetime writes, but its target-phase
  writer histogram and target-gated post-value samples are empty; the
  task/output writer is pre-target.
- H-TaskOutput078EC: the target-phase watch-2 histogram contains
  `0x800078EC`; the known slot writer also publishes task/output data in the
  hangar phase.
- H-TaskOutputOther: the target-phase watch-2 histogram is nonzero but
  contains only a PC other than `0x800078EC`.
- H-CoverageInvalid: the whole-RDRAM threshold, title, hangar, or positive
  phase-bucket control is absent; no target writer null is interpretable.

The discriminator is one watch-2 row keyed by `(lifetime writes,
target-phase VI rows, target-phase writer-PC histogram, post-value samples,
final nonzero/FNV)`. Controls plus a positive `width=512, origin=0x006AB400`
bucket and an empty target histogram select H-TaskOutputPreTarget; a bucket
containing `0x800078EC` selects H-TaskOutput078EC; a nonzero bucket with
another PC selects H-TaskOutputOther; missing controls select
H-CoverageInvalid.

## Exact commands

1. Create the self-contained driver
   `scratch/agent/run_s2295_m5_target_task_output_writer_phase.sh`, based on
   the corrected s2294 oracle paths and eleven named Start presses. Use watch
   indexes 0=`0x0:0x800000`, 1=`0x166000:0x16A000`,
   2=`0x141AD0:0x141AF0`, and 3–18 the 16 `0x300` windows beginning at
   `0x166450` through `0x169150`. Arm `--watch-pc 0x800078EC`,
   `--pc-phase-log-width 0x006AB400:512`,
   `--pc-hist-phase 0x006AB400:512`, `--pc-hist-watch 2`,
   `--post-value-watch 2`, `--post-value-pc 0x800078EC`, `--vi-trace`,
   `--hit-cap 200`, and the natural 120-second oracle shutdown. Retain the
   exact-slot watches as controls; no port process is needed.
2. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2295_m5_target_task_output_writer_phase.sh`

   `zsh scratch/agent/run_s2295_m5_target_task_output_writer_phase.sh`

If any independent control or the width-512 phase bucket is absent, record
H-CoverageInvalid and do not interpret any task/output writer null.
