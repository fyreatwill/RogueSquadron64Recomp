# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: fold s6965_acq_vs34 soaks; then name what re-forms the 21:9 level under ACQ
HYPOTHESIS-ID: g1e-present-drain-acq
s6965: ROGUESQ_PRESENT_DRAIN_ACQ=8 clears the 21:9 level same run (a2: lat 24 vs 39, 0/3 vs 3/3 blocks) at ~0.14 drops/s; the level re-forms every
5-7 s. Head-to-head vs ALT=34 with a level present not obtained (a1 had no level after 40 s).
1. Read SOAK-RESULTS for s6965_acq_vs34_r1/r2 (rings in scratch/s6965q/ring_r1.txt, ring_r2.txt). Score: tools/g1e_drain_blocks.py --from 100,
   acqD/latD counts. Outcome A: level forms in both block kinds; compare lat p50 and drops/s per block kind -> if acq <= 34 on both, ACQ replaces 34
   in OWNER-OPT-INS for 21:9. Outcome B: no level in either -> null, requeue once.
2. Then offline on scratch/s6965/ring_a2.txt: what precedes each level re-formation in a2 on blocks (acq>5 run start)? Join Q rows' wl_ms/tp_ms and
   the G1B log (game task gaps, log_a2.txt) at the run starts vs random times. H-hitch (a game-side late frame lets the queue fill), H-vsync-phase
   (present phase drifts against vsync; acq grows smoothly), H-burst (two presents in one vsync). Discriminator: interval of the 3 presents before each
   run start vs baseline.
Owner reports override all of this. Defaults: DRAIN, DRAIN_ACQ, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE stay opt-in, owner decides.
