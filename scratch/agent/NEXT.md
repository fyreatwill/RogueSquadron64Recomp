# RESUME: exact-range guest-store attribution for F5 terrain vertices
HYPOTHESIS-ID: g3c-owner-visual
s6330 qualified the VTX hook, but the fixed p6 `mprotect` witness is not an exact guest-store witness: its only phase-6 hit was `phys=0x733378`, annotated `guest_pc=0x8000D3D0`, which resolves to `sw v0,0x14(sp)` and is unrelated to the target buffer.

Before building, inspect the existing generated guest-store hook (`rs64_m5_writer_parity`/`RS64_S5798_ST`) and add a bounded shadow callback that records only stores overlapping the most recent phase-6 VTX range (writer PC, address, width, bytes). Keep all A/B arms in one build/run. The shadow must have an ordinary-store positive control in the same run; do not interpret zero target hits without it.

Hypotheses: H-copy (a later guest store writes RGB into the loaded VTX range), H-otherfn (another terrain builder writes the range), H-ucode-light (no guest RGB store; F5 shading supplies the visible colour), H-readback (RDRAM bytes are red but the presented target differs).
Discriminator: for each phase-6 VTX range, the shadow's last-writer table must join to the exact source bytes before the F5 task. A later RGB writer plus red terrain selects H-copy; a distinct terrain writer selects H-otherfn; no RGB writer while F5 output changes selects H-ucode-light; red source bytes with non-red framebuffer output selects H-readback. If the ordinary-store or VTX controls fail, fix qualification before interpreting nulls.

Commands: `cmake --build build --config Debug --target RogueSquadron64Recomp`; then run the existing keyed level-1 DD3 recipe with `ROGUESQ_EDGE_FORCE_RED=1`, `ROGUESQ_LOG_F5_VTX=1`, the new store-shadow env, and framebuffer dumps. Do not add a fade/cull mitigation.
