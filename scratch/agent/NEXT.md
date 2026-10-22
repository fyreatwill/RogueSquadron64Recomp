# NEXT: G1 — find the input that actually moves the player, then re-test ground-troop range gate
s5820: autopilot su-heavy schedule barely moved the player (plxz 43.39,45.95 -> 43.24,45.74); mission ended ~353 s and the s5818 instrument crashed in endMissionCleanup (fixed by 300-event cap, needs rebuild: regen via fixup_game_funcs.py then cmake).
Hypotheses: (a) throttle (not stick) drives player motion -> need autopilot key for throttle/boost; (b) player is in a scripted autopilot segment ignoring stick; (c) stick works but game time per update is tiny.
Discriminator: one run logging player xz every ~60 VI for 3 key schedules phase-gated within a single run (su-only, throttle key only, none), plus raise [rng] per-ra cap per phase. Control: a schedule segment with no keys must show ~0 movement.
HYPOTHESIS-ID: g1-mission-progression
