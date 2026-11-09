# NEXT: cut the gfx-thread host glue so dense scenes (L1 21:9 dd4 WIDEWIN) stay under one VI (G5e/G1c headroom, s7015)
HYPOTHESIS-ID: gfx-host-glue
Context: s7015 WIDEWIN is free on L15 21:9 and L4 16:9, but L1 21:9 dd4 drops 60.0 -> 58.1 fps (P(>=2VI) 0.03, rsp 13.5 ms on). s7014's gfx-thread
profile: rs64_dpc_record_submit (src/rsp/dpc_bridge.cpp:5893) ~7% with about 12 separate full-stream walks (rect_wrap, pillar, spike, region...),
bridge self 8%. Most of those walks exist for diagnostics or for default-on fixes (CULL_SPIKE is default-on and must stay).
Step 1 (code read, one Bash batch): list every walk in rs64_dpc_record_submit and its env gate; classify as diagnostic-only (log/dump flag) vs
needed by a default-on fix. Step 2: early-out each diagnostic walk when its flag is off (cached getenv), and fuse the needed ones into one pass if
cheap. Add ROGUESQ_GLUE_TOG=1 (old path on odd mach 24e6 seconds, emits [s7010-clk]) for a same-run split.
Hypotheses: H-glue (record_submit walks are a real share: rsp mean drops >= 0.5 ms with the trim), H-rt64 (the RT64 RDP decode dominates, trim moves
< 0.3 ms), H-noise (parity noise ~0.5 ms hides it: need p90 and P(>=2VI) too).
Run: env NOCAP=1 ASP=21:9 CULL=1 zsh scratch/s7015/arm.zsh 1 4 G1 "ROGUESQ_G1E_TL=$PWD/scratch/s7016/tl_G1.bin ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_GLUE_TOG=1" 120 200
(copy arm.zsh to scratch/s7016 and fix paths; anchor from run.log; g5e_cost_by_parity.py --skip-s 130, plus --shift-ms 500 control).
Positive control: before trusting a null, check output parity with the trim: CULL_SPIKE count/frame and a captured-frame diff must be unchanged.
Outcome: rsp drop >= 0.5 ms and P(>=2VI) -> 0 on L1 -> land default-on; else record the null with the control and move to the next G-ladder item.
