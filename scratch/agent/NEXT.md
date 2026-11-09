# NEXT: G1c — what makes clampGridCellLookup's per-call cost climb ~40 -> ~130 ns over a dd6 hold
HYPOTHESIS-ID: g1c-dd-headroom
Context (s7024): getGridCellValueAt time = 97-98% the off-map clamp branch (b1, ~6500 calls/frame at dd6 cap 10240). Bounded flat
index (CELLIDX=3, now default at dd>1) ties the std index (113.7 vs 112.9 ns, same run, tog3), so the container is not the cost.
Both modes climb in step over the hold (per-line b1 ns in scratch/agent/m6/g1_lvl1s7024AB2/run.log: 2:45 3:35 ... 2:150 3:150).
G5i: fixed, owner look only. Check CURRENT-TRUTH item 1 first.
Hypotheses:
 H-mem: cache/DRAM misses on the game's record reads (validate: record +0x18/+0x1A/+8/+4, prev +6, s0 +0x16/+6). The 65536 x 0xB8
   pool (12 MB) fills during flight, so hits spread out. Predicts: the time sits in the validate reads, it tracks the pool high-water
   record index, and a same-run prefetch of the next cell's record (or no-validate CHECK-style arm, timing only) cuts it.
 H-host: host call overhead (pre/post out-of-line calls, tick, done()). Predicts a flat ~40 ns with no drift; refuted if the drift is
   in the validate segment.
 H-miss: the miss path (imiss -> L_80048AC4 create: processGridCellByDistance + nested gv + record link) grows with flight. Predicts
   the drift follows imiss/ihit per frame, not per-hit time.
Discriminator, ONE build, ONE run (scratch/s7024/run3.zsh AB arm recipe, CELLIDX=3 fixed, S7022_ST=1): inside rs64_s6963_pre time
 (a) entry -> before validate, (b) validate reads, (c) everything else of b1 (b1 total minus pre), per [s7024-gv] line; plus ihit/imiss
 per stream call and the max record index seen (r). Outcome: (b) carries the drift -> H-mem (then try a prefetch arm with a same-run
 tog); (c) carries it with imiss rising -> H-miss; flat everywhere -> H-host.
Ceiling: b1 ~0.75 ms/frame at dd6. dd4 (the owner's setting) is ~60 fps already, so stop this thread once the drift is named
 and anything that fixes it has been tried in one same-run arm. Then go back to the ladder (G1c phase 2 / owner items).
