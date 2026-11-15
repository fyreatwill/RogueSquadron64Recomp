# NEXT (s7385)
HYPOTHESIS-ID: render-to-rdram-double-pass

s7384 closed class AZ (tools/s7384_static_state_census.py --check rc 0, 0 default-path races) and measured as a side datum
that RT64 draws every frame's raster scenes TWICE: State's FramebufferRenderer inside send_dl on the Gfx thread
(fullSync renderToRDRAM pass; RT64 default framebuffer.renderToRAM = true, lib/rt64/src/common/rt64_emulator_configuration.cpp:13)
and WorkloadQueue's on "RT64 Workload" (26002 vs 25998 submitRasterScene calls in 200 s, ROGUESQ_S7384_LOG=1).
s4905/s4906 put that pass (fsRender + fsRenderSync) at ~6-8 ms of Gfx-thread time per frame, inside the send_dl that bounds
the port's frame rate. Nobody has tested whether the game NEEDS the readback.

Work unit: one opt-in knob, two arms, one comparison.
- Add ROGUESQ_RENDER_TO_RAM=0 (default unset = RT64 default on): set emulatorConfig framebuffer.renderToRAM = false where the
  RT64 application/config is built (src/main/rt64_render_context.cpp; find where EmulatorConfiguration is filled). lib/ edits
  -> ./submodule-patches/export.sh + commit.
- Hypotheses: H-needed (the game reads framebuffers back from RDRAM: pause-menu snapshot/blur, hangar holo, cutscene fades,
  s6206 "rt64wb" copyNativeToRAM spans; the off arm shows black/stale/garbled images there),
  H-redundant (no visible difference; the off arm's send_dl wall drops by ~6-8 ms and G1b/G5c frame time improves),
  H-partial (needed only in specific scenes: then a per-scene / per-fb-pair gate, not a global off).
- Discriminator (one recipe, run twice, same keyed route: env SECS=200 zsh scratch/s7326/run.zsh <name> '<env>'):
  per arm: Gfx-thread submitRasterScene calls (ROGUESQ_S7384_LOG=1: Gfx Thread calls must be 0 in the off arm = knob
  positive control, >0 in the on arm), rt64wb copy count (ROGUESQ_LOG_G1D_TASK=1 [g1d] wb lines), send_dl wall
  (ROGUESQ_S4265=1 or the g1e R lines), crash count, and framebuffer captures at fixed VI phases (title, hangar SELECT YOUR
  CRAFT, mission flight, pause menu, mission intro cutscene) for an on/off contact sheet the owner can judge.
- Outcomes: H-redundant -> offer ROGUESQ_RENDER_TO_RAM=0 in docs/OWNER-OPT-INS.md as a frame-time opt-in (default stays
  on until the owner says); H-needed -> name the scene and the guest reader (write-watch the copied span), park;
  H-partial -> design the narrow gate.
Do NOT change the default. Owner save read-only (runner exports ROGUESQ_NO_SAVE_WRITE).
