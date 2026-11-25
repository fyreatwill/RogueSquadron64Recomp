# NEXT (s7910)
HYPOTHESIS-ID: g3-preflight-load-cue
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, docs/OWNER-REVIEW-QUEUE.md answers,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7909): the port's +28 pre-flight frames on m11 = ONE load stall 86 VI after press 7 (retail 77 VI, port 20 VI;
tools/s7909_window_vi.py scratch/s7872/rdt/oracle.log.zst scratch/s7905/s7905_island_b_rep3/p1/run.log --end-ret 5171).
All other frames 2-VI both sides. port[1916:2559] is exact 643/643 at its own offset, port[2559:2963] (404 vs retail 376)
matches nothing: the scene content forks ~1286 VI after the load.
Work unit (one iteration, then close the pre-flight thread either way): what clocks the fork at port 2559?
Hypotheses:
  H-vicue: a scene step keyed on elapsed VI / osGetTime (not frame count) -> fires 57 VI = 28 frames earlier in port frame
    terms. Predicts: the fork frame's retail VI - load-end VI == port VI - load-end VI (same elapsed VI from the load end).
  H-audio: keyed on the audio clock / music cue (AI DMA count) -> same elapsed AUDIO time, check [ai] or AI counter.
  H-input: press 8 (VI-scheduled) leaks earlier (should not: press 8 is at port fs 2625 > 2559) -> refuted if fork < press 8 frame.
Discriminator (offline first): retail VI of frame r2488 (s7872/rdt per-frame rows: index of row = retail frame - offset;
  calibrate with the 643 segment start r1845 = port 1916) vs port dt7835 VI of port frame 2559; equal elapsed VI from the
  stall end on both sides -> H-vicue; otherwise compare AI counters. If H-vicue/H-audio: CLOSE as retail load-time cost
  (faster loads are fine, owner goal is not load-time fidelity) and record it in CURRENT-TRUTH item 0; take the next
  ladder rung / owner queue.
