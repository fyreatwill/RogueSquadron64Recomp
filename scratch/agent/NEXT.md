# NEXT: FPS60 near-wall flicker: how many RDP triangles each near-cell TRI_GEN produces, episode vs flight
HYPOTHESIS-ID: fps60-wall-rsp-clip
Context (s7105): every near-eye terrain cell in the distance list is emitted by renderFlatMeshFaceGroup 0x8001108C as one 0x28-byte F5 TRI_GEN
(0x05) command on every frame of all 4 episodes, lod byte and w0 constant (H-emit-skip, H-lodswap refuted). s7098: the wall is absent from the
RDP stream. So either the F5 ucode drops the triangles (near clip/reject with the eye at or inside the wall) or the wall is not grid terrain.
Unit (one build, one run, same arm as s7105 plus the new flag):
  scratch/s7099/arm.zsh 6 4 s7106a "ROGUESQ_G1E_LIMIT=1 ROGUESQ_G1E_WIN=600 ROGUESQ_G3C_LOG=1 ROGUESQ_S7101_CHASE=$PWD/scratch/s7106/push_a.txt
    ROGUESQ_S7104_CELL=1 ROGUESQ_S7105_EMIT=1 ROGUESQ_S7106_RSPTRI=1" 120 240
 1. Read docs/F5-UCODE-REFERENCE.md (TriGen: 0x05 -> table 1 -> L_15AC -> overlay selector L_1268) and the recompiled ucode
    (build/factor5_ucode/*.c, hooks only via tools/fixup_factor5_ucode.py; regen per tools/ucode_regen.sh, rerun s7091 `verify` after).
 2. Hook the ucode command dispatch: at each command fetch note the command's DRAM address (DL read pointer) and the RDP output position;
    triangles for a command = RDP tri commands (0x08-0x0F) written between its fetch and the next fetch. Keep a host table addr -> tris.
 3. Extend apply_s7105_emit.py: also store the cmd DRAM address of the 9 ring<=1 cells (ctx->r2 at the rfm visit), and at the next ce flush
    print their RSP tri counts (field t=). Flight comparison per cell, episode vs flight.
 Positive control: far lod-2 (flat) and lod-0 cells must show their fixed counts (GLideN64 TriGen0000 default order = 32 tris) in flight;
 a "mark everything" sum over all TRI_GENs per task must equal the task's total RDP tris (within non-TRI_GEN commands).
Hypotheses:
 H-clip       the eye-cell / ring-1 TRI_GEN tri count drops (toward 0) on episode frames while flight stays at the fixed count -> the ucode
              near-plane clip/reject; then compare the same command against GLideN64 HLE math (eye inside the cell's height field)
 H-elsewhere  near-cell tri counts are unchanged across episodes -> the wall is not grid terrain (object/prop mesh or a cell beyond +-3);
              next: tag RDP tris by source command for the wall's screen region on an episode frame
 H-rdp        counts unchanged but the triangles' screen coords are degenerate/outside on episodes (log the emitted tri bbox too)
Fallback if the ucode hook cannot attribute cleanly: offline H-clip math from a dumped frame (the cell's 25 heights + MVP: any vertex with
w < near on episode frames only).
Default stays retail.
