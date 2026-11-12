# NEXT (s7231): cut the dd6 21:9 cost in the L4 heavy window (s7230: flat 30/s, 20.5 ms gfx task vs 13.9 ms at dd4 21:9)
HYPOTHESIS-ID: dd6-wide-heavy-window-cost
Context: s7230 closed owner-path headroom for dd4 (all owner settings + busy host 2.7-3.7 ms margin). The OWNER-OPT-INS farthest-view
line (DRAW_DISTANCE=6 DD_UNSAFE=1 DD_MELT=1 DD_WIDEWIN=1 ASPECT=21:9) drops L4 to 30/s at t=77-97 (and 2-6 s bursts to t=224).
Hypotheses for where the +6.6 ms goes: H-cells (kept cells/frame ~1200 after the K0.6 off-map cull; cost linear in cells, s7019-s7029),
H-tris (the far ring cells are high-LOD meshes: verts/tris per cell rise, not the cell count), H-clip (far cells straddle the
guard band / near plane and cost clip work in the F5 ucode), H-cap (WIDEWIN cap 10240 is the binding term: cells hit it).
Discriminator, one build, one run: dd6r recipe with a same-run toggle every 10 s (phase-gated) between cap 10240 and 8192 and between
KLEVEL 4:0.6 and 4:0.5, logging per second [g1b] sd_wall + [s7034] kept/f + gfx task vtx/tri counts (check which ROGUESQ_* counter
gives tris per task before building anything new). Outcome: sd_wall tracks kept/f -> H-cells (then a frame-time governor that trims
the far ring only when the last N tasks exceed ~15 ms); tracks tris at equal cells -> H-tris (far-ring LOD down); neither -> H-clip.
Run: env R=$PWD/scratch/s7231 HOLD=240 ARMS="6:dd6r:ROGUESQ_FORCE_SAVE_MISSION=4+ROGUESQ_FULLSCREEN=0+ROGUESQ_ASPECT=21:9+ROGUESQ_RETINA=0+ROGUESQ_DD_UNSAFE=1+ROGUESQ_DD_MELT=1+ROGUESQ_DD_WIDEWIN=1+ROGUESQ_G1B=1+ROGUESQ_STORE_DIAG=0" zsh tools/g1e_owner_quiet_arms.zsh
Score: python3 tools/s7230_headroom.py scratch/s7231/log_*.txt ; python3 tools/s7229_flat30_cost.py ...
Visual bar: any fix must keep the L4 far-left shoreline (s7052 sheet) and the L12 soft band (s7047). Owner path only.
