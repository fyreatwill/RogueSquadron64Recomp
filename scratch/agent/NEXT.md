# NEXT: level-scoped K=0.5 for L12 at 21:9 (keeps L4 at K=0.6)
HYPOTHESIS-ID: dd6-219-l12-levelK
Context: s7055: L12 21:9 dd6 bundle runs 54-55 fps (P(>=2VI) ~0.10) at cap 10240 or 12288; the cap is not the limit.
s7050: K=0.5 on L12 21:9 +0.9/+0.7 fps with frozen poses 0.00 vs K=0.6. s7051 reverted K=0.5 globally because L4 21:9 shaves a far-horizon band.
A per-level K would take L12's gain without L4's loss.
Hypotheses:
 H-levelK: a level-gated K=0.5 (L12 only, FB wider than 16:9) gives L12 +>=0.7 fps same-run, L12 poses <=0.05, L4 unchanged (K stays 0.6, [s7037] log shows 0.6).
 H-noread: the current level cannot be read cheaply at bundle time (bundle runs at startup before level load) -> needs a per-frame K switch in the
   upstream_compat.cpp cull (g_rs64_s7030 path) keyed on a guest level byte; find the byte first (owner save current-mission byte, ROGUESQ_FORCE_SAVE_MISSION
   path, s5705-s5720 recipes) and verify with a same-run log line on L4 and L12.
 H-other-levels: K=0.5 visibly shaves other levels too (only L1, L4, L12 were posed) -> restrict to L12 and record.
Unit: (1) grep the K read site in src/main/upstream_compat.cpp and the level byte (grep PORTING-STATE 'current-mission byte', 'FORCE_SAVE_MISSION');
(2) add ROGUESQ_DD_OFFMAPCULL_KLEVEL=<lvl>:<k>[,...] (default "12:0.5" only when FB_WIDTH>796, explicit _K wins), log [s7056] level=%d k=%f once per change;
(3) same-run check: L12 21:9 hold with tog3 KLEVEL on/off/on via scratch/s7055/run_hold.zsh pattern; L4 21:9 short hold confirming k=0.6; frozen poses L12 (s7050 recipe).
Owner-gated items (G5a-G5i, L15 21:9, G1d) still need nothing run.
