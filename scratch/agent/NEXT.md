# NEXT: G1 — which button kills, and is counter 8 the win condition?
s5824: with real input (A held + B/Z presses, no invuln) counter 1 reached 8 and the mission ended cleanly.
Hypotheses: (a) B fires lasers and produces the kills; (b) Z does; (c) kills come from the approach alone/ambient allies. Discriminator: two runs of g1_fire.sh variants with the SAME A-alternation, one with only B in the fire slots, one with only Z (and a third, A-only, full length), compare ctr1 set count by t=360. Positive control: the A-only run must show fewer sets than the better arm. Also check the 0x620400 screen/result (win vs death) via fbd dumps in m6/s5824_fire/fbd.
Also: regen/rebuild so apply_s5818 cap lands (avoid end-of-mission crash).
HYPOTHESIS-ID: g1-mission-progression
