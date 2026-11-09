# NEXT: G1c — L4 repeat of the off-map fog-depth cull (s7034: K=0.6 near-invisible + rsp -3.04 ms -> 60 fps on L1)
HYPOTHESIS-ID: g1c-offmap-fogdepth
Context: s7034 ROGUESQ_DD_OFFMAPCULL_K (src/main/upstream_compat.cpp rs64_s7031_cell). L1 21:9 dd6 WIDEWIN cap 10240 MELT FPS60, _H=off:
frozen poses K=0.6 0.01-0.18 (void poses 0.18/0.17 vs ungated 10.6/39.0, control 3.6-4.0), cost rsp -3.04 (54.8 -> 60 fps). K=0.8 clean but -0.56 only.
L4 is the open level (94x94 map, 62% off-map cells, s7031 R=2 rsp -3.71 only).
G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14).
Hypotheses:
 H-general: on L4 K=0.6 is also <= ~0.2 at every frozen pose with rsp win >= 1.5 ms (L4 has less off-map waste) -> offer as owner opt-in (OWNER-OPT-INS.md).
 H-L1only: L4 shows a visible void/wedge at K=0.6 (> ~1.0, control-scale) -> L4's far terrain is less fogged (fe vs map size); try K=0.7/0.8 or per-level K.
 H-nowin: L4 image clean but win < 1 ms -> opt-in helps only L1-like levels; still offer, state the per-level win.
Work (no build needed):
 1. Frozen poses: LVTAG=L4k + level 4 in scratch/s7034/run_L1k.zsh (check how g3_optin_pose_arms.sh takes LV; s7031 used LV=4; FZ poses must be re-picked for L4
    from an offA pass, or use the s7031 L4 pose list if one exists). Arms offA, r2k06, r2k07 (K=0.7), r2 (void control), k03. Score s7032_pose_cull_score.py --sheet.
 2. Cost: zsh scratch/s7034/run_cost.zsh K68L4 4 0,0.6,0.7 ; g5e_cost_by_parity --phases 3 --skip-s 130 on tl_K68L4.bin.* + scratch/agent/m6/g1_lvl4s7031K68L4/run.log.
Outcome map: H-general -> add the opt-in line to docs/OWNER-OPT-INS.md (default stays off), close the G1c dd6 headroom thread. H-L1only -> pick the K that is clean on both.
