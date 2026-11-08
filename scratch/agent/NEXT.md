# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — name what preempts the USER_INTERACTIVE Gfx thread at 21:9 late presents (s6978: QoS no help at 21:9, lates still H-rsp-host).
HYPOTHESIS-ID: g1e-gfx-preemptor
Hypotheses: H-intra (our own process: RT64 render/present/texture/shader threads or the game/audio threads saturate the 5 P-cores at that instant),
H-extern (another process: WindowServer/compositor at 21:9 fullscreen, agent/browser), H-ecore (the thread is migrated to an E-core, not preempted).
Instrument (ONE build): sampler thread at 1 kHz (USER_INTERACTIVE) reading thread_info(THREAD_BASIC_INFO) for every task thread
(task_threads) -> per-thread cpu_usage + run_state + name into a ring; plus host_processor_info per-CPU ticks (P vs E cluster load) per ms.
Dump binary at exit (env ROGUESQ_G1E_THREADS=<path>), join to g1e_late_leg.py late instants via mach time.
Discriminating outcome at each H-rsp-host late (wall-cpu gap): sum of our runnable threads >= P-core count -> H-intra (fix: lower QoS of RT64
background threads / pin worker counts); our threads idle but P cluster busy -> H-extern (owner-host issue, document); gfx thread running but
CPU rate low with E cluster busy -> H-ecore. Positive control: the sampler must show the gfx thread running during normal send_dl intervals.
Recipe: s6977 Q0 (21:9 dd4 FPS60 VI_LOCK=1 GFX_QOS=1) 2 runs via soak queue. Defaults unchanged; owner decides GFX_QOS default (16:9).
