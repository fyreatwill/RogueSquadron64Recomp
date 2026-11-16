# NEXT (s7433)
HYPOTHESIS-ID: default-probe-bookkeeping

Fold new scratch/agent/SOAK-RESULTS.md lines first (s7428_audio_route_arms: rc 0 = F9 gate two-arm verified; 2 = VOID; it is at 4/5 voids).

Class CP (CURRENT-TRUTH Next steps item 1). s7432 closed CO H-free: the default-on fprintf calls cost 0.3% of one core and
silencing them (ROGUESQ_DIAG_QUIET=1) moves nothing. But the probes' NON-printing work still runs every call: tables,
counters, guest peeks (e.g. [s5855] sphere-probe table update per call, printing every 1024th; [s5908] caller table;
osViSetMode guest_u32 peeks + dladdr; s3290/s3294 stall-probe bookkeeping). tasks/s is pinned at 60 at FPS60 and a 1 ms
guest busy-wait did not move it, so tasks/s cannot see this; measure guest-thread CPU time per frame instead.
Step 1 (offline, static): census every tools/apply_s*.py / fixup insert compiled into RecompiledFuncs: for each, is it gated
by an env read once (cheap) or does it run unconditionally; is it a diagnostic or a needed guard (guards stay). Classify
all; no runtime yet. Positive control for the census: the [s5855] probe must classify "ungated diagnostic".
Step 2 (one build, one run): per-swap guest-thread CPU time (thread_info THREAD_BASIC_INFO user+system on the thread that
calls osViSwapBuffer) and gfx-thread CPU time, as a [diag-cpu] line per 10 s; gate the ungated diagnostic bookkeeping behind
rs64_diag_quiet (reuse s7432's flag and ROGUESQ_DIAG_QUIET_TOGGLE in-run, ROGUESQ_DIAG_BUSY_GUEST_US=500 as the control
toggle). H-free: guest CPU ms/frame differs < control/4 -> close. H-cost: >= 0.25 ms/frame -> gate those sites by default
(probes become opt-in), after grepping scratch/agent/*.sh and tools/*.sh for every tag they parse.
Runner: env S7431_ARM=P zsh tools/s7431_stderr_volume.sh 320 ROGUESQ_G1E_AQ=2 ... ; analyzer tools/s7432_diag_quiet_ab.py (extend).
