# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — split the residual 21:9 late class: H-slowcore vs H-ucode-work (one instrument, one build, QoS on/off arms).
HYPOTHESIS-ID: g1e-late-cpu-inflation
State (s6981): with STDERR_ASYNC on, GFX_QOS=1 removes Gfx preemption gaps (0 vs 0.7-8.6/min) and lates 1 vs 4 in ~7.8 min.
Every residual late (s6980 Nr1/Nr2, 4/4) has send_dl thread CPU 10.5-11.8 ms vs normal p99 9.5 and 4-10 of 15 CPUs >80% busy.
Hypotheses:
- H-slowcore: same ucode work, the Gfx thread ran on an E-core / lower clock while the host was busy -> CPU ms per ucode step up.
- H-ucode-work: that frame's gfx task really executes more RSP instructions (dense scene second) -> steps up, ms/step normal.
- H-cache: other busy threads on the same P cluster evict L2 -> ms/step up on a P core (CPU id P, steps normal).
Instrument (ONE build): add to each ROGUESQ_G1E_GRING R row (a) RSP ucode steps executed in that send_dl task (counter already
in the LLE loop, cf. ROGUESQ_UCODE_CAP), (b) CPU number at task start and end (Apple Silicon: read TPIDRRO_EL0 low bits as
_os_cpu_number does; positive control: values must span both perf levels over a run with a busy-loop helper on all cores,
and match sysctl hw.perflevel0/1 CPU ranges). Score: per late, steps vs normal p99, ms/step vs normal, CPU perf level.
Arms queued as soaks: 21:9 dd4 FPS60 VI_LOCK, QoS 0 and 1, 330 s, same scorer (tools/g1e_gfx_qos_ab.py --split-at 178.8,
guard now 0 for sham), tools/g1e_late_leg.py, tools/g1e_thread_census.py.
Outcomes: steps high + ms/step normal -> H-ucode-work (scene cost, not host; nothing to fix host-side);
ms/step high on E-core -> H-slowcore (QoS already the lever; propose GFX_QOS default to owner);
ms/step high on P core -> H-cache.
Owner: GFX_QOS default still the owner's call (OWNER-OPT-INS row says 16:9 and 21:9 now).
