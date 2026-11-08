# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e commit term: fast path for RT64 LoadBlock TMEM copy (lib/rt64), with an equivalence arm
HYPOTHESIS-ID: g1e-dd4-rt64-texload
s6956: the commit (~3.4 ms/task at dd4) is RT64 fullSync texture work. Under the commit (scratch/s6956/xt_x.xml, tools/g1e_xt_under.py):
loadBlockOperation 23.5% leaf (inlined loadToTMEMCommon<RGBA32=false,BLOCK=true> per-8-byte-word loop with dxt counter and xor swizzle,
lib/rt64/src/hle/rt64_rdp.cpp:815), TMEM hashing ~30% inclusive (XXH3 update 18.8%, hash lambda 24.2%), uploadTexture 32%.
Unit: ROGUESQ_G1E_LBFAST (default after qualification; =0 old loop; =tog 10 s blocks; =check runs both into a scratch TMEM copy on every
block load and counts mismatches, check #1 against a deliberately corrupted copy = positive control). Fast path: for BLOCK, non-RGBA32,
compute each run of words between dxt swaps (dxtIncrement known per load: run length = ceil((0x800 - counter)/dxt)), copy the run with
memcpy into TMEM (handling the tmemMask wrap by splitting), and apply the tmemXorMask (0 or 4) as one 32-bit-swap pass when set. dxt==0
means one run of all words. Keep the 2048 word cap.
Hypotheses: H-copy (the per-word loop is the cost: expect com -0.5 to -0.8 ms/task, leaf share collapses) vs H-mem (time is cache misses
reading RDRAM: fast path saves little). Equivalence must be bad=0 control=1 before timing counts.
Run (two runs, same build): env OUT=scratch/s6957 zsh tools/g1e_xt_flight.zsh c 240 "ROGUESQ_G1E_LBFAST=check" then
env OUT=scratch/s6957 zsh tools/g1e_xt_flight.zsh t 360 "ROGUESQ_G1E_AQ=3 ROGUESQ_G1E_LBFAST=tog ROGUESQ_G1E_TRING=$PWD/scratch/s6957/tring.txt"
(add an lbfast TRING column or reuse cdiag's slot; tools/g1e_batch_arms.py --arm).
lib/ edit => ./submodule-patches/export.sh + commit same session. Then the TMEM hash: s6942's memo keys on g_rs64_tmem_gen which every load bumps, so check how often a hash re-runs on byte-identical TMEM.
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
