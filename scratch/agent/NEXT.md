# NEXT (s7441)
HYPOTHESIS-ID: rt64-perdraw-diag

Class CX (CURRENT-TRUTH Next steps item 1). One build, one measuring run.
Step 1 (offline): grep default-on rs64_* / getenv-latched calls in lib/rt64/src/render/rt64_framebuffer_renderer.cpp,
hle/rt64_state.cpp, hle/rt64_framebuffer.cpp, hle/rt64_framebuffer_manager.cpp, hle/rt64_present_queue.cpp,
hle/rt64_rdp_tmem.cpp, hle/rt64_workload_queue.cpp. Classify per call frequency (per draw call / per texture / per frame)
as GATED / UNGATED-NEEDED / UNGATED-DIAG (read every consumer).
Step 2 (change, same build): rs64SkipDraw (rt64_rdp.cpp) -> inline static env latch + slow path; any UNGATED-DIAG per-draw
hook found in step 1 gets a call-site latch (ROGUESQ_G1E_TRIM=0 = old path).
Measure: env S7431_ARM=CX zsh tools/s7433_probe_cost.sh; then the top-of-stack python pass used in s7440 (PORTING-STATE)
against scratch/s7440; copy samples to scratch/s7441. Positive control = the probe script's DIAG_BUSY toggle (must PASS).
Outcomes: H-small (all < 0.03 ms/f -> close the diag-cost family for lib/rt64), H-hidden (a hook >= 0.05 ms/f -> gate it,
show its samples drop), H-needed (feeds a default-on fix -> keep, document). lib/rt64 edit => ./submodule-patches/export.sh.
