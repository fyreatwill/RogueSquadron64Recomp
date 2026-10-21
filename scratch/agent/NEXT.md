# NEXT: what do mtm mode-3 store (0x800FB2B0 val=3) and the 0x100 setter (0x800EE85C) mean — does a non-god mission actually end?
s5758: bit1 = player-slot-0 spawn event (benign). Unexamined in s5757 log: [mtmst] 0x800EE85C val=0x100 x4 (tickSongFadeTimer, funcs_40 0x800EE730) and 0x800FB2B0 val=3 x2.
Task (offline, no build): disassemble funcs for 0x800FB190 (handler ids 1-3) and 0x800FB2B0 region in funcs_42.c; read what word the val=3 store targets and who consumes it. Read 0x800EE730 timer: what are floats 0x8010C300/C304 and byte 0x8010C262/264/262, and is the 0x800957AC gate = audio query (0x800A0F50 flag)?
Hypotheses: H1 mtm stores 3 into a mode word that ends the mission (real end path, stalled by non-god timing); H2 val=3 is an unrelated state (objective stage) and no end ever fires in the keyed route; H3 0x100 timer is audio/song-fade dependent (M5 artifact) and gates something.
Discriminator: consumer of the val=3 word + whether any later code reads it to start the transition; for H3, whether 0x800957AC depends on audio state we stub.
Control: reuse s5757 run.log lines 718887/725967 as ground truth; any new soak must show >=1 [mtmst] 0x800EE85C line.
HYPOTHESIS-ID: g1-nonhealth-fail
