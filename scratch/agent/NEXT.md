# NEXT: owner-path fps of WIDEWIN at 16:9 and on L1/L15, then offer it to the owner (G5e, s7014)
HYPOTHESIS-ID: dd-wide-window
Context: s7014 showed WIDEWIN cap 8192 costs no fps at 21:9 dd4 L4 on the owner path (58.5-60 fps, two runs); the s7010-s7013 cliff was the harness
probe path (LOG_PHASE). Before telling the owner it is free, check the other aspect and two more levels with the same instrument.
Hypotheses: H-free-everywhere (all arms P(>=2VI) <= 0.05), H-level (a denser level, L1 or L15, crosses the VI at 8192), H-aspect (16:9 differs).
Discriminator: one tog run per arm (OWNER_TIMING defaults to 1 in scratch/s7014/arm.zsh; check run.log shows [g1e-fast] on=1 / [g1e-probes] on=0):
 env NOCAP=1 ASP=21:9 CULL=1 zsh scratch/s7014/arm.zsh 1 4 L1 "ROGUESQ_G1E_TL=$PWD/scratch/s7015/tl_L1.bin ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=tog" 120 200
 then L15 (needs ROGUESQ_FORCE_PLANET_UNLOCK=0xFF) and L4 at ASP=16:9. (Copy arm.zsh to scratch/s7015 first and fix its paths.) Raise the watchdog or
 DU so the harness summary gets written. Split: python3 tools/g5e_cost_by_parity.py <tl>.<pid> <anchor> --skip-s 130 (grep the [s7010-clk] line
 out of run.log before deleting it). Positive control: rsp on > off by ~2 ms (s7014 +2.26 at 8192 vs 4096).
Outcome: all clean -> report to the owner via OWNER-OPT-INS (recommend WIDEWIN with dd>=2 at wide aspects; default stays the owner's call). A failing
arm -> name the level/aspect and measure rsp vs run to say which term crosses the VI.
