# M5 s4930 route reinitialization census

The bounded source census found one identity-construction site in
`src/main/main.cpp:4026-4100`. `rs64_audio_route_prepare` clears the current
identity, accepts the committed VI phase, and constructs the next identity at
line 4082. The ordinal is produced only by `g_rs64_audio_ordinal.fetch_add(1)`;
the row is produced only by `g_rs64_audio_phase_row++`, reset when the
width/origin key changes. No other assignment constructs an identity.

There are two direct prepare callers: `musyx_stub_probe` and
`factor5_ucode_b_probe`. `rs64_log_audio_return` has one lazy prepare path,
but only when the identity is already invalid. `rs64_m5_route_prepare_handoff`
in `upstream_compat.cpp` only records the prepare/VI-commit relationship; it
does not write the identity. The only normal invalidation is the audio-return
clear. This exhausts the route-identity writer/prepare class.

The rebuilt binary was run with `scratch/agent/s4923_mission_longevity.sh`.
Controls passed: mission origin `0x690400`, advancing `update_screen` 6656 to
13888 over 120 seconds, 47 transition controls, 2,124 transition events, and
zero crash/abort markers. The route log contained 435 rows at `0x690400` and
363 at `0x620400`; all sampled rows used `factor5_ucode_b`. The first observed
handoff changed from ordinal 1541/row 5 at `0x690400` to ordinal 1547/row 0
at `0x620400`, with later `0x620400` re-prepares likewise starting at row 0.
PCM source and consumer rows were present in the run (41 and 154 at the
`0x690400` origin under the existing phase-gated log). The route/task/PCM
transition stream therefore shows a new Factor5 task publication, not a
port-only ordinal write or label-only discontinuity.

Conclusion: H-legitimate-publication is selected at the port level. This does
not claim retail parity for the exact ordinal scheme, and authorizes no guard,
skip, or route suppression.
