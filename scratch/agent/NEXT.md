# NEXT (s7901)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7900): island B = flame-jitter rand values misaligned by the s7896 per-site ordinal replay key. Burst-keyed replay
(tools/s7896_rand_replay.py --burst 600 + ROGUESQ_RAND_REPLAY_BURST=600, APM=1) on m11: crawl tail 298 -> 68 non-exact frames
(alternate frames, 1 tri each), post-crawl cinematic 473 -> 0, flight exact 2667/2667. Arms kept: scratch/s7900/m11apm (burst off),
scratch/s7900/m11burst (burst on), retail s7895/m11k/r1 (oracle.log was decompressed to s7900/m11apm/r1 and removed; re-decompress).
Unit (one build, offline first):
  1. Residual: in scratch/s7900/m11burst/p1_rand.txt vs scratch/s7900/replay_m11k_b600.txt, find calls whose (site,burst,bord) has
     no table row or a different seed (post-replay) in the crawl-tail VI window, per site. Candidates: H-b0 (0x800541FC burst 0 is
     16 retail vs 416 port calls -> burst index shift for that site), H-res (retail burst boundary at 1 s [vi] resolution), H-other
     (a third site). Run tools/s7900_tri_source.py on one residual frame (needs a s7751 snapshot: ROGUESQ_S7751_SNAP +
     ROGUESQ_S7751_EVERY around port frame 5640..5780) only if the rand census does not name it.
  2. Fix in the replay table/key, rerun the m11burst recipe (scratch/s7900 command in the s7900 ledger entry), expect crawl tail 0.
  3. Then m6 (0x31=5) with APM=1 + burst replay (its island B N212 should go the same way), and look at the APM-only pre-flight
     N2398@567 texrect/HUD block (present in both APM arms, absent in the old-schedule map).
