# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: fold soak s6963_cellchk, then the 21:9 present level
HYPOTHESIS-ID: g1e-dd4-dense-tail
s6963 fixed the LEVEL=4 dense-second tail: clampGridCellLookup chain walk indexed (ROGUESQ_G1E_CELLIDX default on at dd>1; tog A/B 60.00 vs 58.94
tasks/s, 0 vs 9 slow seconds; CHECK=2 23.4M compares 0 bad, control 23494/23494).
1. Read SOAK-RESULTS for s6963_cellchk (lvl1 21:9 and LEVEL=10, CHECK=2). rc=0 = exact on both: close slug g1e-dd4-dense-tail.
   rc=1 with a real mismatch: read the "[g1e-cell] BAD" lines in scratch/s6963ck/log_*.txt (s0, x, z, walk vs idx). A stale miss means some other code
   links records into a template chain; find the writer of +0x6 for that s0 (grep RecompiledFuncs for stride 0xB8 users of *(0x80137A5C)) and either
   hook it or default to mode 1 (hits only, misses walk). Until fixed set the default to 0 in src/main/upstream_compat.cpp (S6963 ctor).
   rc=2 = human active: requeue from done/.
2. Then, if G5 is still waiting on the owner: the lvl1 21:9 present level (acq>5 ms 45.6%, lat p50 37.7). Hypotheses: H-drawable (nextDrawable wait
   with 3 drawables at 2389-wide), H-gpu (GPU frame > 16.7 ms at 21:9 dd4), H-pace (present timing vs vsync phase). Discriminator: per-present
   acq_ms vs gpu_ms in ring_w21 (tools/g1e_owner_hz_score.py + one python pass): acq high with gpu < 12 ms = H-drawable/H-pace; gpu > 16 = H-gpu.
Owner reports override all of this. Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE stay opt-in, owner decides.
