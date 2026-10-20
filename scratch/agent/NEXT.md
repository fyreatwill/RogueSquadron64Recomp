Single next work unit (s5629): fold s5628_snap_{a,b} ([ccosnap] lines in scratch/agent/m6/s5628_snap_*/run.log) — G1 find WHY the idle ship fails at ~+342 s.
Static fact (s5628): 0x64=1 fires when bool[0x65]==0, bool[1]==1, bool[0x63]==0, bool[7]==1, bool[0x64]==0 (lv2_checkComplexObjectives 0x80101F08-FB0); bool array at 0x8013889F+id.
Hypotheses: (D) bool[7]/bool[1] flipped by ship death; (T) timer/escort flag flips at fixed time; (S) bool[1],[7] are set at start and the 0x65 time-gate is the trigger.
Discriminator: timestamps of 1/7/0x63/0x65 in [ccosnap] vs +342 s. Positive control: snapshot #1 present at first cco call. Then find the writer of the flipping id (grep setObjectiveBooleans callers / direct MEM_B to 0x801388A0 range) and make the soak survive (god-mode / stick input).
HYPOTHESIS-ID: m6-mission-endurance
