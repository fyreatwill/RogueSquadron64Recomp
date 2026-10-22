# NEXT: G1 — what ends the mission (s5824 ended at ctr1=8; s5825 arms did not)
s5825: B-only 6, Z-only 6, A-only 8 ctr1 sets, none ended (alive_at_end=1). Kills come from approach alone.
Hypotheses: (a) mission end needs ctr1==8 AND another objective/timer (b) s5824 end was run-specific (ship position/time) (c) the s5824 end was a death/other path, not a win. Discriminator: grep s5824 run.log vs s5825_aonly run.log around ctr1 set #8 and origin 0x620400 transition for end reason (endMissionCleanup caller/args); positive control: s5824 log contains the transition.
Also: regen/rebuild so apply_s5818 cap lands.
HYPOTHESIS-ID: g1-mission-progression
