# NEXT: G1d widen the identified menu/hangar video-state calls
HYPOTHESIS-ID: g1d-widescreen

s6166 names the writer: `buildAndRegisterDefaultMaterial` at guest PC
0x80017C14 stores the video-state width source 0x8011A838. Its menu/hangar
calls use `(a0,a1)=(0x200,0x154)` or `(0x280,0x154)`; the existing s6113
opt-in hook only rewrites `(0x200,0x1C0)`, the flight call. Wide phase 5 still
emits CI width 512 and 2048x1360 scissor with VI width 796.

Work unit: change the regeneration-safe s6113 hook in
`tools/apply_s6031_far.py` so `ROGUESQ_FB_WIDTH` rewrites only the identified
menu/hangar 512-wide calls (the 0x154-height forms) in addition to the already
qualified 512x448 flight form. Reapply to the live generated tree, build once,
and run the same level-1 4:3/16:9 pair with `ROGUESQ_LOG_RDP_ROUTE=1` and
`ROGUESQ_FB_DUMP_VI=1` until two phase-5 samples per arm are captured. Keep
the default retail path unchanged; do not alter RT64 allowlists.

Competing hypotheses and discriminator:
- H-menu-video-state: rewriting the 0x154-height calls makes CI/scissor follow
  the wide VI and the hangar dump become valid.
- H-menu-display-list: the opt-in writer rewrite leaves phase-5 CI/scissor at
  512; the 512 values are emitted later by a separate display-list builder.
- H-present-stride: CI/scissor become wide but the dump remains garbage; this
  selects a downstream buffer/present defect.

Positive control: the unmodified writer trace must fire in both arms and the
wide arm must reproduce the known phase-5 tuple (CI 512, VI 796). Commands:
`cmake --build build --config Debug --target RogueSquadron64Recomp`; run the
qualified level-1 pair from `build/` with OSMEM 8 control and OSMEM 12,
ROGUESQ_ASPECT=16:9 wide, using title origins 0x790400/0xB52200 and mission
origins 0x690400/0xA52438. Kill both test processes with SIGKILL after the two
phase-5 samples; compare route rows and fbdump validity.
