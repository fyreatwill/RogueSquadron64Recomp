# NEXT (s7907)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7906): island B = deterministic two-class outcome. det_frame_cmp offset gap (main vote vs the 643-frame pre-flight vote)
28 -> crawl exact, 29 -> crawl-tail residual (soaks resubmit the previous odd-stream DL at crawl task 2665, one task late to ~2885).
Sim ticks, dt and task/frame interleave are identical between classes; host load is not the selector.
Work unit: locate the 643-frame segment and the one-frame boundary shift.
  1. Fold rep3 (if it ran: its p1.bin.zst is kept). If it is gap 29, use it; else C2/D are gap 28 refs (C has p1.bin.zst).
  2. Extend tools/s7868_det_frame_cmp.py (opt-in flag, default byte-identical) to print the port index range of each offset vote
     cluster; run on a gap-28 and a gap-29 run -> which port phase holds the 643 votes and which boundary between it and the crawl
     gains/loses a frame (compare phase start indices and [phase] at-VI / press VIs from p1.out / run.log).
Hypotheses:
  H-press: an APM press lands on the other side of a game-frame boundary (VI-clocked presses vs boot-dependent frame phase);
    fix = phase-gated/frame-clocked press for that one press (harness), then the crawl is exact in every run.
  H-game: the shift is a real port-vs-retail timing difference in a scene transition (e.g. a load or fade one frame longer);
    then it is a port defect to name (writer of the scene timer) not a harness fix.
Discriminator: if the shifted boundary coincides with a press VI (within 1 frame) in gap-29 runs only -> H-press; if it sits at
  a non-press scene transition -> H-game.
Budget: if this does not name the boundary in one iteration, close island B as "harness-alignment-dependent, flight exact" and
take the next CURRENT-TRUTH Next-steps / G-ladder item.
