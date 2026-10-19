Work unit: read s5496_dbc_names soak (scratch/agent/m6/s5496_dbc_a/lldb_att1.log): per datItemSetObjectiveBooleanCount hit, caller bt + r4-r7/r16-r18. Name the three NPCs bumping 0x80138064 to 3. If bp never hit, check the 0x3470 positive control first.
Hypotheses: (L) scripted ambush destroys 3 protected objects (legit); (X) runtime misfires destruction (bad collision/timer).
Discriminator: same three identities at same frames across runs, and damage precedes them => (L). Alternative: firing autopilot to see if flight outlasts frame 8000.
HYPOTHESIS-ID: m6-mission-endurance
