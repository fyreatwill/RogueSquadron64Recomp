# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e: fold the locked owner figure at current defaults, then take the top remaining commit term
HYPOTHESIS-ID: g1e-dd4-commit-leaves
s6961 ranked the commit leaves (TMEM hash 26.1%, loads ~21%, setup <3%) and landed ROGUESQ_G1E_HGATHER (default on, exact, commit -0.117 ms/task).
Commit is now ~3.09 ms/task median (dd4 16:9 windowed flight). Queued soak s6961_locked_hgather (locked 60 Hz fullscreen owner figure, current defaults;
s6942 defaults read 58.8 fps). First read its SOAK-RESULTS line and log (tools/g1e_sync_rate.py / g1e_owner_hz_score.py output in the soak log).
- If >= 59.5 fps and 0 crash: the dd4 16:9 sync rate is at the cap; close slug g1e-dd4-commit-leaves, record it in CURRENT-TRUTH, and move to the
  owner's open items (CURRENT-TRUTH Next steps; G5 rows waiting on owner) or the next ITERATION.md ladder rung that is not closed.
- If below: the remaining commit is texel memory traffic (rs64LoadBlockRuns 15.3% leaf, hash scan + XXH3 over ~2 KB per upload) and RT64 draw
  recording/AGX encode (~20%). Hypotheses: H-traffic (loads + hash read the same ~2 KB twice: fuse the CI4 TLUT scan into the LoadBlock copy, or hash
  straight from the source run, byte-equivalence checked like s6957/s6961) vs H-encode (recordFramebuffer/submitRasterScene per draw call dominates:
  CALLER=submitRasterScene tools/g1e_xt_leaves.py on scratch/s6961/xt_x.xml first, no new run needed). The offline split of xt_x.xml decides which.
Owner reports override all of this. Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE stay opt-in, owner decides; HGATHER is on (=0 restores).
