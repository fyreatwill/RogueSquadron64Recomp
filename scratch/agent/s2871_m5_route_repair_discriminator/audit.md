# Session 2871 route-repair discriminator

| control | last qualified | current pair | result |
|---|---|---|---|
| build cwd/binary/ROM | `build/`, Debug target, local ROM | same paths and present | match |
| LLE route | force, ungated, solo | same | match |
| M4 width | `ROGUESQ_M4_Y8000_WIDTH=512` | omitted | drift restored |
| phase gate | `512` | `1024` | drift restored |
| key handling | phase-relative, leave capture running | phase-relative, no leave flag | drift restored |
| audio arms | silent and image | silent and image | match |

The restored-control A/B was one Debug build and two concurrent
`tools/probe.sh` arms. Both reached `VI 640 @ 0x0066A500` and emitted 47
`[audtask-dispatch]` markers, but neither reached `VI 512 @ 0x006AB400`;
neither emitted `[CRASH]` or `[ABORT]`. The capture was SIGKILLed after the
route remained stable, so no downstream audio null is interpreted.
H-config-drift is rejected as sufficient; H-route-state is selected.
