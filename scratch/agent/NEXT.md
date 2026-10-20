Single next work unit (s5637): determine who invokes sayWhoaHim_v0x1FC (0x80108388) and whether its voice-line event precedes the 0x64 LOSE arm. (Carried over from s5636, which was a maintenance iteration; CURRENT-TRUTH is now 13.8 KB.)
Hypotheses: (A) the voice-line script table is stepped by an in-mission timer/proximity trigger, and the fail arm is a separate cause that merely co-occurs; (B) saying the line is a consequence of an ally/player-damage event that is the real fail cause; (C) bool 7 is only read by the checker as "player heard warning" gating the LOSE.
Discriminator: grep the ROM/data tables and recompiled code for address 0x80108388 (lui 0x8010 / addiu -0x7C78 or table words) to find the dispatcher; then log playObjectiveVoiceLine1 calls (positive control: the 0x1FC call itself fires in a failing run) in the next soaks; also classify the 3 setObjectiveBooleans call sites for id 7.
Outcomes: dispatcher is a timer/proximity step -> A; fires only after a damage/kill event -> B; no caller before LOSE yet bool read by checker -> C.
Related: G2 -- voice lines produce no audio; playObjectiveVoiceLine1 is the dialogue entry to trace.
HYPOTHESIS-ID: m6-mission-endurance
