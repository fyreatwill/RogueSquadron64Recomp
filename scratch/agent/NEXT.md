# NEXT: fold s5737_phase{a,b} (phase/lives/B14 watch) and classify the mission exit
Read scratch/agent/soak_results/s5737_phase{a,b}_*.log `grep '\[phase\]\|\[god3\]\|\[god-dead\]'`. Control: [phase] lines exist at all (init transitions at mission load).
Hypotheses: (H1) death path: 0x10CA20 ->1 with hp<=0, 0x130B10 decrements, ->3 when lives hit 0 (game-legit: idle autopilot gets killed; then G1 needs real flying input, not a bug). (H2) phase 3 with hp>0 and lives>0: objective/timer path requestMissionTransitionMode(3|2) - find the caller (function-pointer table). (H3) lives start at 1 in our save/init so first death = game over (check 0x130B10 initial value; compare retail default).
Arm b (revive) discriminates: if phase still goes 1/3 with hp pinned >0, the death is not health-driven.
Then: if H1, move G1 to real-input flying (survive via sticks/fire) or lives poke as a PROBE; if H2, watch caller via lldb on 0x800FB190.
HYPOTHESIS-ID: g1-gameover-cause
