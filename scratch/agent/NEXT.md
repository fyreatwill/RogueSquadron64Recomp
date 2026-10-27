# RESUME: pre-VTX last-writer attribution for F5 terrain vertices
HYPOTHESIS-ID: g3c-owner-visual

Checkpoint close-out for s6332: do not rerun s6331. Resume the work unit below
as the next iteration; the existing artifact is
`scratch/agent/m6/g1_lvl1s6331_vtxshadow2/run.log`.
s6331 qualified the post-VTX shadow: the ordinary-store control fired in phase 4, the VTX control fired in phase 6, and a clean DD3/red level-1 hold produced zero phase-6 overlaps. The 96 overlaps were phase 7 and all wrote zero. This is not a writer null because the terrain buffer may have been populated before the VTX task, or by a bulk copy outside the parity hook.

Before building, extend the existing generated guest-store hook (`rs64_m5_writer_parity`) with a bounded physical-address last-writer table populated before phase 6. On each qualified VTX callback, join every word in its source range to the most recent writer (PC, width, value, phase) and dump the source bytes. Add a bulk-copy census/control for the same range in the same build; retain the ordinary-store and VTX controls. Do not interpret a null unless both controls and the bulk-copy control fire.

Hypotheses: H-precopy (the range was filled before the F5 task), H-bulk (a memcpy/unaligned path bypasses parity), H-ucode-light (no guest RGB writer exists), H-readback (source bytes are red but presentation is not).
Discriminator: every phase-6 VTX range must join to a last writer and exact source bytes. A pre-VTX RGB writer selects H-precopy; a bulk-copy witness selects H-bulk; no writer with non-red source while the red arm remains non-red supports H-ucode-light; red source bytes with non-red framebuffer supports H-readback. If a control fails, fix qualification before interpreting nulls.

Commands: `cmake --build build --config Debug --target RogueSquadron64Recomp`; then run the keyed level-1 DD3 recipe with `ROGUESQ_EDGE_FORCE_RED=1`, `ROGUESQ_LOG_F5_VTX=1`, the last-writer/bulk-shadow env, and framebuffer dumps. Do not add a fade/cull mitigation.
