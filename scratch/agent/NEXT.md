# NEXT (s7897)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7896): m3 island B CLOSED as H-rng (RAND_RESEED / det_pair RREP=1 -> m3 pre-flight exact 544/544). m6 B N212@6071 and m11 B
N1054@6069 survive a full per-site retail rand replay (scratch/s7896/m6q, m11q: SNAP=3 + SNAP3_ONLY=c + REPLAY; bins + rand kept).
Both start at retail frame ~5538 (port 6069/6070) with the same signature: a few PRIM FFFFFFFF tris move, count grows (m11 to
~600/frame). Same retail frame on two missions = shared content after the chapter crawl.
Unit:
  1. Offline: map retail frame 5538 to a VI and to a scene: which 0x800C6674 / 0x800AF374 marks bracket port frame 6069 in
     scratch/s7896/m11q/p1_rand.txt (port rows carry VI; RDP bin frame -> VI via the [vistamp]/phase in p1/run.log), and which
     timeSnapshotFiller struct (s0) those frames use (s7895 list: 80165DE0 = crawl). Is B inside the crawl or the next scene?
  2. Hypotheses: H-dt (one more frame in that scene stores a different dt than retail: the s7891 crawl-clock family), H-object
     (advanceNpcOnCurvedPath / walker progress differs by call count, m6 0x8006C0FC runs 81 vs 80), H-cam (camera spline phase).
  Discriminator (ONE run, both missions share it so use m11 = largest island): `zsh tools/s7891_crawl_clock.sh scratch/s7897/cc
  EEP=scratch/s7895/m11k/lvl.eep SECS=130 SNAP=3` with P1-equivalent ROGUESQ_SNAP3_ONLY=c (check the script passes it; add an XE/P1E
  hook if not) and score with tools/s7891_crawl_clock_cmp.py: the first per-call dt/struct row that differs from retail after the
  =c frame names the frame. If it falls at the B start -> H-dt, pin it like =c (key by struct). If every dt row is retail-equal
  through B -> H-object/H-cam: dump the FFFFFFFF object's state (find it from the differing tris' screen position) instead.
Notes: scratch/s7894/p1only.sh does NOT expand SNAP=c (use SNAP=3 P1E=ROGUESQ_SNAP3_ONLY=c), det_pair.sh does.
