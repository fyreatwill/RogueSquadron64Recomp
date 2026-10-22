# NEXT: G1 - s5852: do survivors die if fire is held while the player dwells at them?
s5851: autopilot passed within ~1 u (xz) of survivors 0x1f,0x20,0x21,0x26,0x28 without killing them (tools/analyze_lv0_player_vs_targets.py). plpos btn is 1 Hz so fire exposure is unmeasured.
Hypotheses: H1 no fire pressed while near (autopilot fire schedule misses); H2 fire pressed but bolts not aimed at ground troops at close range (bolt dir horizontal at player altitude, s5834; targets y -2..-4 vs player -6.5); H3 NPCs not alive at pass time (despawned/respawned).
Discriminating measurement: one run with ROGUESQ_AUTOPILOT holding B (fire) continuously from mission start (g1_fire.sh variant) + ROGUESQ_LOG_PLPOS at higher rate or per-VI btn; offline join with kills. Decisive: if kills of passed-by survivors rise with continuous fire -> H1; if not -> H2/H3 (then log bolt min distance at close range).
HYPOTHESIS-ID: g1-mission-progression
