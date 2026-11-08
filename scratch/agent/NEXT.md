# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — fold 21:9 GFX_QOS=1 replicas (s6976_219_gfxqos1_r1/r2, results in scratch/s6976w; tail prints
# g1e_gfx_qos_ab.py + lock score). 16:9 replicated s6976 (late ~1.2/min -> 1 in 7.3 min, sham control flat).
HYPOTHESIS-ID: g1e-gfx-thread-qos
Outcomes: 21:9 after-windows late ~0 -> QoS1 holds on both owner screens; update OWNER-OPT-INS row ("21:9 check queued" -> result).
21:9 after == before -> aspect-specific (21:9 late presents were drawable-queue level, s6962-ish): note it in the row.
Either before-window with no gap>3 and no late -> no positive control for that run; use the sham split on a no-QoS 21:9 ring.
Then: remaining drops under QoS1 (G1r2 had 1 entry at 219 s): join with g1e_late_leg.py to see if they are still descheduling
(gap>3) or a different leg (present/drawable). If different leg -> try QoS on the present thread (same env pattern).
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE, VI_LOCK, GFX_QOS stay opt-in. VI_RT default on.
Owner reports override all of this.
