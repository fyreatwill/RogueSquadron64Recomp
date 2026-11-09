# NEXT: de-bias the same-run tog parity split (s7016 A/A null: odd seconds rsp -0.63 ms with nothing toggled)
HYPOTHESIS-ID: tog-parity-bias
Context: every same-run A/B since s7010 picks the arm by (mach_absolute_time()/24e6)&1 and splits the G1E_TL ring with
tools/g5e_cost_by_parity.py. s7016 run N1 (L1 21:9 dd4 MELT WIDEWIN=1 CULL=1, ROGUESQ_GLUE_TOG=3 = anchor only, no toggle): odd rsp -0.63 ms,
shift 250 ms -0.06, shift 500 +0.49. That is a phase-locked load with a ~2 s period, as large as the effects being measured.
Hypotheses: H-periodic (a game/host workload every 120 VIs, phase-locked because VI is host-timed: a hashed per-second arm assignment removes it),
H-tool (an anchor/clock mapping error in g5e_cost_by_parity.py: then the bias would follow the anchor, not the game, and the per-frame
t_us vs mach mapping is checkable offline against the [s7016-glue] parity rows), H-thread (gfx-thread placement alternates P/E with a 2 s cadence).
Step 1 (offline, no build): in scratch/s7016/tl_N1.bin.* compute rsp per 1 s bucket and its autocorrelation / period spectrum (lags 1-10 s).
A clean 2 s peak -> H-periodic; a slow drift -> neither. Also check whether runs G1/F1/N1 agree in phase.
Step 2 (one build): add extern "C" int rs64_tog_odd(void) = hash32(mach/24e6) & 1 (splitmix-style), with an [s7010-clk] anchor, and use it at
the GLUE_TOG sites first (src/rsp/dpc_bridge.cpp record_submit); add --hash to g5e_cost_by_parity.py using the same hash.
Run: copy scratch/s7016/arm.zsh; arms in one script: A/A null (GLUE_TOG=3 hashed) and positive control GLUE_TOG=1 (skip walks) on L1 21:9 dd4.
Accept when the null |rsp delta| < 0.15 ms and the 500 ms shift collapses. Then move the WIDEWIN/LODMUL/W_CLAMP/... tog sites onto the helper
(fixup scripts for generated code) and re-measure L1 21:9 WIDEWIN cost with the de-biased split.
