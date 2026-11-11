# NEXT: FPS60 near-wall flicker: why the camera push-out lets the near plane into the wall (16:9 corner width?), and fix it
HYPOTHESIS-ID: fps60-wall-nearclip
Context (s7107): the dropped wall is the eye terrain cell clipped by the projection near plane (tags: eye cell 4 -> 1 tri on the
dropped swap, z ~0; presented frames show a straight near-plane cut, docs/owner_sheet_s7107_nearclip_a/_b.png). The camera's
near-plane push-out is applyPlayerVehicleStateUpdate 0x8004CD00 (s7101: 4 corners from the FOV via transformVec3ByMat34, ray test
pos->corner for s4=0..2 only, on hit pos = hit - 2*near*unit(corner-pos)); s7103's re-push of all 4 corners did not help.
Unit:
 1. Code-read (no run): how 0x8004CD00 builds the corner offsets - which FOV / aspect / near constants it reads - vs what the
    projection uses at ASPECT=16:9 (s6142 wide camera, s6144 FP_XSCALE = ASPECT_SCALE, guPerspective near). Write the numbers.
 2. Build ROGUESQ_S7108_CAMWIDE=1|tog (new tools/apply_s7108_camwide.py): scale the corner x half-width by the aspect scale the
    projection uses (and optionally test all 4 corners, reuse s7103's CAMFIX path), =tog in odd mach seconds (same-run control).
 3. Run scratch/s7099/arm.zsh 6 4 s7108a "ROGUESQ_G1E_WIN=600 ROGUESQ_G3C_LOG=1 ROGUESQ_S7101_CHASE=$PWD/scratch/s7108/push_a.txt
    ROGUESQ_S7104_CELL=1 ROGUESQ_S7105_EMIT=1 ROGUESQ_S7106_RSPTRI=$PWD/scratch/s7108/rt_a.txt ROGUESQ_S7107_TAG=1
    ROGUESQ_G5B_TRIS=$PWD/scratch/s7108/tris_a.bin ROGUESQ_S7108_CAMWIDE=tog" 120 240 ; split episodes/stream losses by tog state
    (capture episodes from g5b_drops + tools/s7098_wall_flicker.py rule; stream near-z eye-cell losses from tools/s7107_losscan.py).
    Second arm if time: same with ROGUESQ_ASPECT=4:3 (edit arm.zsh copy) and CAMWIDE=0.
Hypotheses:
 H-aspect   corners use the 4:3 width while the 16:9 projection is wider -> CAMWIDE on removes most episodes / near-z losses; the
            4:3 arm shows few
 H-corner4  the untested 4th corner (s7101) -> the cut sits at that corner's screen quadrant; CAMWIDE alone does not help
 H-neardist the push distance (2*near) vs the projection near differ (e.g. our far/near scaling at dd>1) -> compare numbers in (1);
            dd1 arm still drops (s7098: dd1 FPS60 2 episodes)
 H-tick     the push-out is right but the FPS60 render-only frames use a camera that skipped it -> episodes only in lim1 windows
Positive control: the stream loss detector must still flag the clipped swaps in the off state (s7107 numbers: p99 354 cells).
Default stays retail; any fix is opt-in until the owner judges it.
