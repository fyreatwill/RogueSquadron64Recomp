# NEXT: FPS60 near-wall flicker: log the near-plane push-out per corner at an episode, with a same-run 4-corner arm
HYPOTHESIS-ID: fps60-wall-camera
Context (s7101): camera chain per tick = chase (updatePlayerVehicleByControlMode mode 3, no terrain query) -> near-plane
push-out applyPlayerVehicleStateUpdate 0x8004CD00 -> matrix copy -> terrain builder. The push-out builds 4 near-plane
corners (sp+72/84/96/108 via transformVec3ByMat34), but its loop (0x8004CF0C..0x8004CFC0, `slti v0,s4,3`) ray-tests only
the first 3 (pos->corner, sampleTerrainAtNpcPosition 0x80068D5C). On a hit it sets pos = hit - 2*near*unit(corner-pos)
(addScaledVec3ToVec3 0x800AA3E0, a2 = f20 = 2*near). Then there is a y floor at 0x8004D044. Chase overshoot, craft jitter,
mid-tick read and terrain-origin shift are refuted. The 60 fps per-tick excess is unproven (1.6x, p=0.185).
Recipe: scratch/s7099/arm.zsh 6 4 <tag> "ROGUESQ_G1E_LIMIT=1 ROGUESQ_G1E_WIN=600 ROGUESQ_G3C_LOG=1 ROGUESQ_S7101_CHASE=<file>" 120 240
(no STORE_DIAG: it perturbs the game). Episode tools: s7099_wall_split.py <raw> <csv> <run.log>; s7101_bvread.py; s7101_target_vs_eye.py.
Unit (one build, one run):
 1. PC hooks in applyPlayerVehicleStateUpdate (fixup script like tools/apply_s7101_chaselog.py, same CHASE file): per
    corner i=0..3, log the corner point, the pos before, the hit flag (v0 after the sampleTerrainAtNpcPosition call at
    0x8004CF58), the hit point (sp+16), and the pos after. For corner 3 (never tested), call sampleTerrainAtNpcPosition
    from the hook on a scratch copy, or replicate the call with the same args, to learn whether it is inside terrain.
    Also log the y-floor branch (0x8004D044 taken).
    Positive control: hits > 0 on wall-hug ticks, and the logged pos-after must equal the next ch line's pre-step pos.
 2. Arm ROGUESQ_S7102_CAM4=tog (30 s halves, like s7101_clamp_on): loop bound 3 -> 4 (test the 4th corner as well).
    Default off = retail.
Hypotheses:
 H-corner4  the flicker frames have corner 3 inside the wall while corners 0-2 are clear -> CAM4 removes the episodes
 H-snap     the push alternates between corners or ticks (hit on tick n, miss on n+1) and the near plane crosses the wall
            on the miss ticks -> CAM4 does not help; fix = keep the push active (hysteresis) or push by the full near-plane radius
 H-mesh     all tested rays miss at the flicker frames (collision terrain != visual mesh) -> neither helps; the next probe is the
            terrain sample vs the drawn cell height
Outcomes: per-episode corner table; episode count per CAM4 half (needs a >=2x drop for H-corner4). Owner sheet of before/after
frames if CAM4 wins. The default stays retail until the owner says otherwise.
