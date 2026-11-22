# NEXT (s7818)
HYPOTHESIS-ID: oracle-det-default-and-vu-word
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7817 made the retail oracle deterministic (`--det` = `--clock vi --det-core`; 82/82 2 MB dumps byte-identical across two runs)
and found stock vs patched cxd4 differ by 0 visible px on title->hangar, but by ~1 32-bit word per dump off-screen at ~0x7887xx
(111 halfwords over 41 dumps, scratch/s7817/d1 vs ds).
Unit (one emulator run at a time, CPU rule max 2 heavy jobs):
 1. Bounded change: every oracle launcher that compares runs (grep -l 'rs64_oracle ' tools/*.sh tools/oracle/*.sh scratch-free) gains
    `--det` by default with `ORACLE_DET=0` restoring the old wall-clock/randomized behaviour. Positive control per touched script:
    two runs byte-identical on its dumps (or its own scored output identical).
 2. Name the off-screen word: `--det` run with `--watch 0x00788000:0x0078B000` (physical; arm the whole-RDRAM control first per
    README) in stock and patched; the writer PC (RSP DMA vs CPU) and the structure at that address (z-buffer? matrix/vertex scratch?)
    decide whether the VU defect reaches game logic (H-cpu-read: CPU later reads it -> behaviour can diverge) or is render-only
    (H-dead: written by RSP DMA, never read back by the CPU).
Hypotheses: H-dead / H-cpu-read / H-zbuf (it is a depth-buffer word: render-only, invisible).
