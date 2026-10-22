# NEXT (s5914): steer the ship with the autopilot stick keys, count class-1 crossings

HYPOTHESIS-ID: g1-mission-progression

s5913: stick=0 for all 413 plpos samples; track misses logged class-1 spheres by 1.4-8.8 (radii 0.06-0.68). H-aim selected.
Work unit: copy scratch/agent/g1_fireall.sh to g1_steer.sh; add phase-gated held stick keys (su/sr/sd/sl keys per the s5821 table, e.g. rotate 3s windows) alongside A-fire; raise [sph] log budget if cheap. Run once (420 s), then tally crossings per class-1 id with the s5912 HUDBIT tally (ROGUESQ_LOG_HUDBIT=1).
Control: the unsteered s5912 baseline had 6 class-1 crossings total; any steered run is judged vs that within-run phase (stick-off phase vs stick-on phase, gate on VI).
Outcomes: crossings >6 and rising with steering -> aim confirmed, then closed-loop steering from the player dump; no change -> steering keys do not move the ship (check plpos sx/sy nonzero first) or range (bolt life) limits.
Analysis: python3 tools/g1_track_vs_spheres.py <run.log>
