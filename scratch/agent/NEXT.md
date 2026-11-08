# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — replicate ROGUESQ_GFX_QOS=1 (s6975 single-source).
HYPOTHESIS-ID: g1e-gfx-thread-qos
s6975: residual VI-lock late presents are the Gfx thread descheduled mid gfx task (wall-CPU 4-12 ms, CPU normal). GFX_QOS=1 (QoS UI)
flipped at 180 s: late presents 2.15 -> 0/min, gaps>3 12.2 -> 2.5/min; mode 2 (time-constraint) no help.
Fold soaks s6975_169_gfxqos1_r1/r2 (scratch/s6975r; tail prints g1e_gfx_qos_ab.py + lock score). If not run, run one by hand.
Outcomes: both after-windows late ~0 and gap>3 below before -> H-rsp-host fix replicated: make GFX_QOS=1 default-on? NO — owner decides;
add it to docs/OWNER-OPT-INS.md next to VI_LOCK and ask. Either before-window lacks gaps>3 -> no positive control, rerun.
After == before in both -> s6975 was host noise; next lever: pin RSP work off E-cores is not possible on macOS, so try QoS on the
present thread too, or close as owner-tolerable (~1 drop/100 s).
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE, VI_LOCK, GFX_QOS stay opt-in. VI_RT default on.
Owner reports override all of this.
