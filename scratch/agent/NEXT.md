# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — fold 21:9 QoS-from-start soaks s6977_219_qos0_r1/r2 (results scratch/s6977q; tail prints g1e_gfx_qos_ab --split-at
# 178.8 + lock score). Control already measured: scratch/s6977w N1r1/r2 no-QoS 21:9 = 10 late30-40 in 7.6 min (1.3/min).
HYPOTHESIS-ID: g1e-gfx-thread-qos
Count late30-40 events from 95 s in both Q0 runs (rate*window from both windows), pool (~7.6 min).
Outcomes: pooled QoS <= ~3 events (<0.4/min, Poisson p<0.01 vs 1.3/min) -> QoS helps at 21:9 too; update OWNER-OPT-INS row.
Pooled ~6-10 -> no 21:9 benefit: row says 16:9 only; then run g1e_late_leg.py on the Q0 lates: if still H-rsp-host (wall-cpu gap)
the thread is preempted despite USER_INTERACTIVE -> next lever is fewer competing threads (check what else runs on P cores at those
instants; RT64 present/worker threads at default QoS) rather than more QoS.
Either way this closes the QoS thread; owner decides the default. Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB,
INFLIGHT, PROVCACHE, VI_LOCK, GFX_QOS stay opt-in. VI_RT default on. Owner reports override all of this.
