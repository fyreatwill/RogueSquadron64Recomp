# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e residual lock drops — name the late game frame (s6974 selected H-hitch offline).
HYPOTHESIS-ID: g1e-vilock-late-frame
s6974: every lock-mode drain drop is a real one-vsync level started by a late Q (dQ 21.6-29 ms) + catch-up Q (~10 ms); ACQ8 is correct.
Fold soaks s6974_169_V10g_r1/r2 (scratch/s6974q, V10 lock + ROGUESQ_G1E_TL + ROGUESQ_G1E_GRING). Their tail prints
g1e_lock_arms_score, g1e_drop_context --quiet, and g1e_tl_present.py (kick chain per present). If the soak didn't run, run the same
recipe by hand (one game at a time). Offline: for every late Q (dQ>20 ms after 95 s), print its kick chain from g1e_tl_present.py
(kick gap, kick phase after VI, q, rsp, rdp, game running/blocked split by mq) vs normal presents.
Hypotheses: H-sim (game thread running > 20 ms between the two kicks: a CPU burst in game code, find the function via TL codes),
H-rsp/H-rdp (kick on time, rsp or rdp leg long), H-sched (game blocked on a mesg queue long: VI/SP/DP event delivery late).
The leg that is long on late Qs and normal elsewhere selects. If late Qs are < 1 per 40 s and the leg is game code with no cheap fix,
close the thread as owner-tolerable and record it.
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE, VI_LOCK stay opt-in, owner decides. VI_RT default on.
Owner reports override all of this.
