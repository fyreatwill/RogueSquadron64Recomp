# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: phase-lock the VI timer to the display vsync (even-cadence level onsets at 21:9)
HYPOTHESIS-ID: g1e-vi-display-phase
s6967: the over-budget frames were late VI edges (VI thread default QoS on macOS), fixed default on (ROGUESQ_VI_RT). With RT the 21:9
drawable-queue level still forms: r2 7/7 onsets with even 16.7 ms cadence, a2's level survived the flip. Two free 60 Hz clocks (our
steady-clock VI deadline grid vs the display vsync) drift in phase; when a present lands on the latch edge it misses, the queue goes
one drawable deeper and 60 in / 60 out never drains it.
0. Fold soaks s6967_virt_169_v1/v2 (SOAK-RESULTS.md; tools/g1e_vi_rt_ab.py on scratch/s6967q): VI p90 before/after the 150 s flip on the
   owner 16:9 recipe, and late presents/s before vs after (the 21:9 runs had too few misses in the before window to judge).
1. Boring first, offline on scratch/s6967 rings r2/a1/a2 (RT on, present P rows = display vsync times): measure the drift of
   (Q time - nearest display vsync) over the run, i.e. VI grid vs display period. Expect a slow linear phase ramp; an onset where the
   phase crosses the acquire/latch point. If the phase is flat (display period == our 16.6667 to <1 ppm), H-vsync-phase is refuted ->
   look at what does change at the even-cadence onsets (tp/wl/gpu, compositor).
   Competing: H-vsync-phase (ramp, onsets at a fixed phase), H-compositor (WindowServer/compositor hiccup: P interval 33 ms with even Q),
   H-gpu-late (gpu_ms spike on the onset frame).
2. If H-vsync-phase: ONE build, opt-in ROGUESQ_VI_LOCK=1: VI thread reads the latest presented vsync timestamp (plume presented handler,
   mach clock, same as TL) and slews its start_time by <=0.1 ms per VI toward a target phase (e.g. present Q at vsync - 8 ms), with
   ROGUESQ_VI_LOCK_AT=<s> one-way flip (policy toggles are sticky, s6967) for a same-run before/after. Watch: VI rate stays 60.00 on
   average (audio is per-VI), no runaway when the display is not 60 Hz (only lock when the measured display period is 16.6-16.8 ms).
3. Acceptance: same run, lvl1 21:9 dd4 FPS60, no drain knob: level onsets/min after the flip << before, lat p50 <= 27 ms.
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE stay opt-in, owner decides. VI_RT default on (s6967; =0 old).
Owner reports override all of this.
