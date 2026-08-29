# Session 3143 — M5 port VI edge qualification

The Debug build included the new `[m5-vi-edge]` witness immediately after
the host `VI_WIDTH_REG` write, corresponding to retail ELF edge `0x800357A8`.
The capture used the validated LLE-only/autopilot route and retained the
existing VI-context and host voice-audit controls.

Results:

| Measurement | Result |
|---|---:|
| all-width edge control rows | 8 |
| VI-context control rows | 8 |
| host voice-audit control rows | 1 |
| title `1024 @ 0x00790400` | 0 |
| hangar `512 @ 0x006AB400` | 0 |
| target `[m5-vi-edge]` rows | 0 |
| crash / abort rows | 0 / 0 |

The run reached only the existing pre-title route (`320`, transient `2`, and
`640 @ 0x0066A500`). The controls are positive, but target-phase parity is
unevaluable because the port stopped before title and hangar. This selects
`H-AudioRouteStillBlocked`, rules out neither a target edge mismatch nor a
downstream audio contract gap, and authorizes no audio, route, or VI behavior
change. The newly added probe is single-source port evidence; Session 3142's
independent retail ELF/oracle evidence remains the separate ground-truth line.

Artifacts: `scratch/agent/s3143_m5_port_vi_edge/summary.log` and
`scratch/agent/s3143_m5_port_vi_edge/game.log`.
