# NEXT: G1d locate the menu/hangar width-policy writer
HYPOTHESIS-ID: g1d-widescreen

s6165's phase-5 join trace selected a menu/hangar width-policy mismatch. In the
4:3 control, hangar RDP CI width is 512 and VI width is 512. In the 16:9/12 MB
arm, hangar RDP CI width remains 512 while VI width is 796; wide title and
flight do emit width-aware CI values. The route reached title/hangar/mission in
both arms with no crash markers. The exact writer is still unnamed.

Work unit: one offline census plus one bounded runtime probe to identify the
menu/hangar video-state writer that leaves the RDP CI/scissor at 512 under
ROGUESQ_ASPECT=16:9. First enumerate every SETCOLORIMAGE/SETSCISSOR producer
and the video-state update callsites around the phase-5 submission; then add a
single env-gated writer trace or width-aware opt-in patch, rebuild, and run the
same level-1 control/wide pair until two phase-5 samples per arm are captured.
Do not change the default or patch a generic RT64 allowlist.

Competing hypotheses and discriminator:
- H-menu-video-state: the menu/hangar game-side video-state writer is hardcoded
  to 512. A writer trace at the phase-5 submission identifies the PC/global;
  changing only that opt-in width makes CI/scissor follow 796 and the dump
  become valid.
- H-menu-display-list: the video state is already width-aware, but a separate
  menu display-list builder emits 512 coordinates/targets. The writer trace
  stays width-aware while the RDP stream remains 512; this selects the builder.
- H-present-stride: RDP is valid but VI/present reads a wrong buffer. CI/scissor
  become 796 while the dump remains garbage; this refutes the current phase-5
  mismatch and selects a downstream present defect.

Positive control: the trace must fire in phase 5 in both arms and report the
known control tuple (CI 512, VI 512) and wide tuple (CI 512, VI 796). Commands:
`cmake --build build --config Debug --target RogueSquadron64Recomp`; run the
qualified level-1 pair from `build/` with OSMEM 8 control and OSMEM 12,
ROGUESQ_ASPECT=16:9 wide, using title origins 0x790400/0xB52200 and mission
origins 0x690400/0xA52438. Kill both test processes with SIGKILL after the two
phase-5 samples; compare route rows and fbdump validity.
