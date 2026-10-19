Work unit: name the three destruction-debris NPCs that bump counter 0x80138064 to 3 (lldb bp on datItemSetObjectiveBooleanCount 0x80065914, log a0..a3 + caller + npc+0x34), reusing scratch/agent/m6_objc_stores2.sh. Alternative: firing autopilot to see if flight outlasts frame 8000.
Hypotheses: (L) scripted ambush destroys 3 protected objects (legit); (X) runtime misfires destruction (bad collision/timer).
Discriminator: NPC identity/position and whether destruction precedes any damage source; (L) if the same three die at scripted times each run.
HYPOTHESIS-ID: m6-mission-endurance
