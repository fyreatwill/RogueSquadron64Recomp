# NEXT: fold G1(d) forced-hit arms, then extend (d) across levels 6-18

HYPOTHESIS-ID: g1-mission-coverage-sweep

S5946: lvl1 folded (tools/g1_d_compare.sh 1): TELE 0 vs 10; BooleanCount writes 13->22, objcount id=13 max 4 both arms => partial H1/H3, single-source.
Next unit: run `tools/g1_d_compare.sh N` for lvl2-5 once their soaks land; identify which objcount id is lvl1's real kill counter.

State: (a)+(b) done for levels 1-18; (c) done 18/18 (docs/g1_flight_contact_sheet.png).
Queued: g1_lvl{1,2,3,4,5}_tele (ROGUESQ_TELE_BOLT=1) and g1_lvl{1,3}_ctl.
Logs: scratch/agent/m6/g1_lvl<N>{tele,ctl}/run.log.
Hypotheses per level: H1 TELE fires and objective counters ([objcount]/[objwr]) rise vs ctl => (d) PASS;
H2 TELE never fires ("[sph] TELE" absent; class-1 update-fn key is lvl0-derived) => lever inapplicable,
need per-level NPC update-fn census ([fn41] tally) to retarget; H3 TELE fires but counters flat => objective logic
for that level not reached by player hits (investigate that level's end-gate writer).
Discriminator: tele-vs-ctl count of [objcount]/[objwr] lines plus TELE-line count (control).
If soaks have not run yet, do offline work: write the (d) comparison script (tools or scratch) so the fold is one command.
