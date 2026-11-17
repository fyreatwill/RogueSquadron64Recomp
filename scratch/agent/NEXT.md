# NEXT (s7507)
HYPOTHESIS-ID: fd-rsprecomp-ctrlflow

Context: s7506 fixed the N64Recomp jr/jalr slot-order defect (N64Recomp b684176; BZ tool S4 latch control PASS, HAZARDS 2 -> 0).
The game-side generator is now audited end to end (BZ s7416). The RSP side never was: RSPRecomp (../N64Recomp/RSPRecomp/src/rsp_recomp.cpp)
emits the F5 gfx/audio ucode that runs LLE every frame (build/factor5_ucode/*.c, ~15 files incl. overlays + clip composite).

Work unit: class FD = the BZ audit for RSPRecomp output. One offline tool, tools/s7507_rsp_ctrl_flow.py, over build/factor5_ucode/*.c
against the ucode images (tomls factor5_rsp_*.toml in ../N64Recomp give text offsets/sizes):
 R1 every conditional branch: condition text == op/regs (RSP gprs are 32-bit; bgez/bltz signed), condition evaluated BEFORE the slot
    (if the slot writes rs/rt, the emitted C must latch the compare - check print_branch_condition / print_branch order), goto target ==
    disasm target, slot copy present on both paths.
 R2 jal: $ra written = vram+8 (MIPS writes ra at the jal; slot sees new ra = correct), target label exists.
 R3 jr/jalr: jump_target latched before the slot (already, lines ~523-528); jalr with rd == rs: MIPS reads rs before writing rd -
    emitted `jump_target = rs; rd = ...` order is right; flag any rd==rs site anyway. do_indirect_jump switch covers every jr target
    reachable (resume_targets / overlay entry list) - list switch cases vs label set.
 R4 branch-in-delay-slot / resume_delay paths (lines ~576-599): every R_xxxx_delay label is preceded by the slot it resumes.
 R5 positive controls: synthetic emissions (slot before cond, wrong target, missing latch, 64-bit compare) must each be flagged; mutate
    one real site in a temp copy and require the tool to catch it.
Hypotheses: H-equal (0 defects, like BZ) / H-latent (defects only in unreachable ucode) / H-live (a reachable site reads a reg after its
slot overwrote it -> RSP output differs from hardware: then fix in rsp_recomp.cpp, regen via tools/ucode_regen.sh, diff old/new outputs
must be only the flagged sites, build, one L4 300 s hold, and compare RDP stream vs angrylion on one frame).
Discriminating outcome: R1-R4 defect list split by reachability (ucode task entry + overlay map in PROJECT-OVERVIEW "F5 ucode").
Read docs/F5-UCODE-REFERENCE.md first. No game run unless H-live.
