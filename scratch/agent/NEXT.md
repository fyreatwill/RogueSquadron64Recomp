# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — fold s6980_219_async_noqos_r1/r2 (21:9 VI_LOCK, async stderr on, GFX_QOS OFF), decide whether GFX_QOS still matters.
HYPOTHESIS-ID: g1e-async-qos-residual
State (s6980): async stderr whole-run replicas (with GFX_QOS=1) 1 late in 7.66 min (0.13/min) vs 1.04/min direct stderr; gaps>3 ms 0.
1. Read SOAK-RESULTS for s6980_219_async_noqos_r1/r2; data scratch/s6980q/. Score: python3 tools/g1e_gfx_qos_ab.py
   scratch/s6980q/gring_NrN.txt ring_NrN.txt log_NrN.txt --split-at 178.8 (sum both windows; late30-40/min x dur).
   Hypotheses: H-async-enough (pooled <~0.3/min, gaps>3 ms ~0 -> QoS not needed at 21:9; tell owner the lock recipe needs no QOS),
   H-qos-needed (~1/min with H-rsp-host verdicts in g1e_late_leg -> QoS still helps once stderr is off the Gfx thread; re-run 16:9 pair).
2. Residual class: "none>p99" lates blocked on the VI-ack queue 0x80128CF0 (s6978 Q0r1 3/4, s6980 r1 1/1). If it is the only class
   left, look at what holds the game thread there (VI thread wake vs game frame overrun) using TL+census in the same windows.
3. Owner: GFX_QOS default still the owner's call.
Defaults: STDERR_ASYNC on (=0 off), everything else unchanged.
