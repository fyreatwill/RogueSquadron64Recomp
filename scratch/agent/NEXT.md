# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — the late presents that remain under GFX_QOS=1 on a loaded host: guest game thread preempted (no QoS) vs residual Gfx preemption.
HYPOTHESIS-ID: g1e-late-guest-qos
State (s6982): send_dl CPU inflation on lates = cross-cluster migration of the Gfx thread (home cluster CPUs 10-14, +1.4 ms when it
runs elsewhere, even on perflevel0 5-9); GFX_QOS=1 removes the migration under load. A reproducible late generator now exists:
scratch/s6982/burst 14 1500 3500 started 120 s into scratch/s6982/arm_B0.sh (QoS off, ~40 late/min) / arm_B1.sh (QoS on, 19-31/min).
B1's remaining lates (leg_B1.txt): 18 H-sched (kick phase late = guest thread late to submit), 14 H-rsp-host, 10 H-rsp-?, 64 none>p99.
Hypotheses:
- H-guest: guest game thread (default QoS, ultramodern one-at-a-time hand-off) is preempted by the load, so its gfx kick misses the VI.
- H-gfx-resid: Gfx thread at USER_INTERACTIVE still loses its 5-CPU home cluster to the load (wall-cpu gaps 49-60/min remain).
- H-present: RT64 present/acquire thread is late (present ring at/acq level), independent of both.
Change (ONE build): ROGUESQ_GUEST_QOS=1 sets QOS_CLASS_USER_INTERACTIVE on every guest thread at creation (ultramodern threads.cpp;
default off). Arms under the same burst: B1 (GFX_QOS=1) vs B2 (GFX_QOS=1 + GUEST_QOS=1), same scorer:
tools/g1e_late_leg.py ... --windows, tools/g1e_late_work.py (SUMMARY line), tools/g1e_gfx_qos_ab.py --split-at 178.8.
Outcomes: H-sched lates fall and lates/min drop well below B1's 19-31 -> H-guest (propose GUEST_QOS to owner with GFX_QOS);
H-rsp-host lates and gaps unchanged and dominant -> H-gfx-resid; neither moves and present ring shows acq-late -> H-present.
Same-run control: the burst starts at 120 s, so the 95-120 s window is the quiet control in every arm.
Owner: GFX_QOS default still the owner's call (OWNER-OPT-INS row updated s6982 with the load evidence).
