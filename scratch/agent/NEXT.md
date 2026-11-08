# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e commit term: repeat-load census, then skip load+hash for repeats
HYPOTHESIS-ID: g1e-dd4-rt64-texload
s6957 landed the LoadBlock run-copy (ROGUESQ_G1E_LBFAST default on, -0.225 ms com/task). Remaining commit (~3.15 ms/task at dd4) is still
RT64 fullSync texture work: TMEM hashing ~30% and uploadTexture ~32% of the commit (s6956 xctrace). The s6942 gen-keyed hash memo never hits
because every upload follows a load. Question: how many loads are REPEATS, i.e. same (fmt, siz, src addr, words/rows, dxt, tmem, stride)
as an earlier load AND byte-identical source? If most are, a repeat can leave TMEM as it was known to be after that load and reuse the
cached hash (key = descriptor + content check), skipping both copy and XXH3.
Unit (ONE build, both pieces): ROGUESQ_G1E_LOADREP=stat counts per second in flight: loads, descriptor repeats (direct-mapped table of last
N=4096 descriptors), content-identical repeats (cheap 64-bit hash of source bytes stored per entry), and whether the TMEM state before the load
equals the TMEM state recorded at that entry (needed for skipping). Positive control: a synthetic duplicate (re-issue load #1 once) must count.
Hypotheses: H-repeat (>50% content-identical repeats with equal prior TMEM: build the skip next, expect com -1 ms) vs H-fresh (<20%: textures
really stream; then the lever is uploadTexture itself, e.g. the per-upload GPU copy batching) vs H-partial (repeats exist but prior TMEM differs:
a skip needs per-tile-region tracking).
Run: env OUT=scratch/s6958 zsh tools/g1e_xt_flight.zsh r 240 "ROGUESQ_G1E_LOADREP=stat"
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
