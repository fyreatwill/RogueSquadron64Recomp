# NEXT (s7858)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7857 0x31=14 shows a port-side 1-2 ULP transient in record words 9,15,57,151,159 at ticks 892-899 (retail r1==r2, so not
oracle noise; H-fma refuted). Main split at t1396 is H-audio-clock (closed class).
Unit: name the writer of 0x80137DD4 (w9) at tick 892 on both sides, in one run each.
 - retail: rerun the s7849_det_pair.sh r1 oracle line (see s7857 PORTING-STATE; scratch/s7857/v14/lvl.eep) into
   scratch/s7858/r3 adding `--watch-write 0x137DD4:0x137DD8 --watch-write 0x137FEC:0x137FF0` to XO (val= is the value BEFORE the
   store); positive control: the watch must fire on ticks < 892 too. Map store PCs to tick via the 0x800FA730 rows.
 - port: same recipe as p1 (pinned, DT_AT from scratch/s7857/v14/pins.txt) with a write log on the same addresses
   (grep tools for an existing ROGUESQ_*WATCH* store watch first, e.g. s5690 bool-store / XTRACE). Compare the store sequence
   and the FPR inputs (RS64_ORACLE_FPR) at the first differing store.
Outcomes: same store PC, different input FPR -> walk back one producer; different PC/count -> sub-tick ordering (dt/timing);
 identical stores but different value -> an FPU op mismatch (sqrt/cvt/round mode; compare that op in isolation, s7408 style).
Then continue the sweep: `zsh tools/s7856_det_sweep.sh scratch/s7858 15 16`.
