# NEXT: G1c phase 2 — fold the fog-depth off-map cull into the DD knob, then spend the headroom on a bigger cell pool
HYPOTHESIS-ID: g1c-dd-bundle
Context: s7036 qualified ROGUESQ_DD_OFFMAPCULL=2 _H=off _K=0.6 at 21:9 dd6 WIDEWIN cap 10240 (L1/L4/L5 ~505 s flight, 0 crashes, rsp -2.8/-1.3/-1.3 ms).
G1c spec: "Bundle the winning combination behind the single ROGUESQ_DRAW_DISTANCE knob". Cells are clamped at POOLX<=5 (10240) in
src/main/main.cpp rs64_g1c_apply_dd_policy (line ~12034), so dd6 and dd8 draw the same window (s7019).
Step 1 (code): in rs64_g1c_apply_dd_policy, when dd>=6 and DD_WIDEWIN is on and ROGUESQ_DD_OFFMAPCULL is unset, default it to 2 / K 0.6 / H off
 (log one line "[s7037] dd bundle offmapcull=2 k=0.6 (auto)"); any explicit env wins. dd<=5 unchanged, default dd1 unchanged (retail).
 Check how OFFMAPCULL reads its env (grep ROGUESQ_DD_OFFMAPCULL src/) so the default is applied before that read.
Step 2 (experiment, same build): allow POOLX 6 (12288 cells) behind ROGUESQ_DD_POOLX_MAX=6 (opt-in), and run L1 dd8 21:9 WIDEWIN with the bundle,
 tog3 cap 10240/12288/12288 (ROGUESQ_DD_WIDEWIN_CAP=10240,12288,12288 WIDEWIN=tog3) via a copy of scratch/s7036/run_hold.zsh.
Hypotheses:
 H-room: 12288 cells with the cull stays >= 59 fps on L1 (rsp <= ~12 ms) and shows more terrain (side-third edge score, g5e_edge_score.py phases=3) -> next step up.
 H-cliff: 12288 crosses the VI cliff again (P(>=2VI) > 0.1) -> dd6 + bundle is the max; close phase 2 with an owner sheet.
 H-limit: the window does not grow at 12288 (trace 17 dims unchanged, 128-col cap) -> the next limit is the 128 stride; document it.
Score: python3 tools/g5e_cost_by_parity.py --phases 3 --skip-s 130 <tl> <run.log>; crashes from scratch/s7031/crash_<N>.txt; needs NOCAP unset for edge scoring (capture ~5 GB per 110 s at 640x274: keep the hold at 110 s).
