# NEXT (s7706)
HYPOTHESIS-ID: wide-fb-readback-fold-s7706

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.

1. Fold the queued soaks s7705_fbread_L4_21x9 and s7705_fbread_L4_16x9 (SOAK-RESULTS + scratch/s7705/L4_*): each prints
   `tag=fbread_L4_<aspect> alive= crash=` and the `summary ... ctl_boot_in= fresh_in_after_boot=` line of tools/s7705_join.py.
   Expected (H-none): fresh_in_after_boot=0 at 21:9; at 16:9 skipped_bufs may be 0 (no wild widths) -> ctl_boot_in=0 and rc 1 is then
   "no skip at 16:9", not a failed control (check skipw=0 in the tag line). If a fresh IN hit appears: run the s7704 poison arm
   (tools/s7704_wide_fbcopy_arms.zsh, ARMS="pskip", POISON=<width>) on that scene and look for magenta.
   If the soaks have not run yet, run one in-session: `env LV=4 AS=21:9 O=$PWD/scratch/s7705/L4_21x9 zsh tools/s7705_fbread_flight.zsh`.
2. Then take the next open ladder rung (3c): G3 render fidelity, in-flight frame diffs vs a retail framebuffer (angrylion/oracle) at 4:3
   L1 — check PORTING-STATE (grep angrylion, s6785) for the existing capture route before building anything.
