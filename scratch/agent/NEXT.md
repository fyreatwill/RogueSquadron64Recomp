# NEXT: G1 - s5845: does the forced-hit kill chain reach mission WIN? (end-to-end with forced geometry)
s5844: TELE gated on class-1 update fn (ctx+0 in 800cabd4/800d93c0/800e7860) gives 24 sends, counter-1 sets 13 (vs 4). Win not seen in 320 s.
Step: run env ROGUESQ_LOG_HITS=1 ROGUESQ_TELE_BOLT=1 ROGUESQ_LOG_HUDBIT=1 zsh scratch/agent/g1_fire.sh s5845 700 (autopilot fires only 240-400 s: extend fire window in g1_fire.sh to 240-640 first, e.g. loop seq 360 3 637 with 'a'). Look for [ctr1] c=N past 13, objective-complete / win VI change.
Outcomes: counter plateaus below threshold -> find the remaining objective counters (2,3 in c=a,b,c); win fires -> then build real-input steering toward class-1 NPCs (replace TELE).
HYPOTHESIS-ID: g1-mission-progression
