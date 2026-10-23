# NEXT: G1c - fold s6043_dd2w tblwatch (run by loop between iterations)
HYPOTHESIS-ID: g1c-draw-distance
Retail control (s6044): tbl 0x80136DC4 only goes nonzero->nonzero (3 tblwatch lines), death churn also in retail (lives=12736) => churn is not the dd2 cause.
Discriminator: grep '\[tblwatch\]' scratch/agent/m6/g1_lvl1g1cdd2w/run.log. If a line shows ->00000000: name the writer (the transition line gives call#; watch write PC of 0x80136DC4), H2 confirmed, fix at root (what dd2 knob/clamp makes the loader free the table). If no zero line but crash persists: tbl==0 was a symptom of a different fault; take lldb backtrace of dd2s SIGBUS in streamTerrainGridCellsByDistance+10880.
Positive control: first line FFFFFFFF->initial must print.
