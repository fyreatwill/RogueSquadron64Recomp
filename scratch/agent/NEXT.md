# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e commit term: rank the remaining commit leaves at current defaults, then take the top one
HYPOTHESIS-ID: g1e-dd4-commit-leaves
s6960 closed the provenance hash cache (exact, but per-load tagging 104 ns x 2.3 loads/hash > hash saved; d_com +0.075 ms/task). Commit is
still ~3.1 ms/task (median, dd4 16:9 windowed flight). s6956 xctrace put 26.9% of Gfx samples under the commit, before LBFAST (s6957).
Unit (ONE run, offline analysis): env OUT=scratch/s6961 XT=1 zsh tools/g1e_xt_flight.zsh x 240 "" (xctrace 30 s attached at ~t165,
current defaults). Export the Time Profiler table (xcrun xctrace export, as in s6956/s6957 analysis) and rank the leaves under the commit
(RT64 fullSync / uploadTexture / loadToTMEMCommon / TMEMHasher::hash / hashSet / queueGPUUploadTMEM / draw-call setup) by self samples.
Hypotheses: H-hash (TMEMHasher::hash still the top leaf -> the only route left is a cheaper hash, e.g. CI4 NEON further, not skipping)
vs H-load (loadToTMEMCommon tile/TLUT paths dominate -> a LoadTile/TLUT run-copy like s6957's LoadBlock fast path, byte-equivalence
checked like s6957) vs H-setup (per-draw-call state/hashSet/unordered_map work dominates -> a cheaper container or batching).
The ranked leaf table selects; build the fix for the winner in the same iteration if it is a bounded change, with =tog and an
equivalence check. If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md) comes first.
Owner reports override all of this. Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE stay opt-in, owner decides.
