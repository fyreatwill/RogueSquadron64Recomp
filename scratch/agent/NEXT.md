# NEXT: [mtm] fold s5753 soak verdicts (table dump + mask-change log)
Soaks s5753_mtma/mtmb are queued (loop runs them). Read scratch/agent/soak_results/s5753_*.log: grep '\[mtm\] TABLE\|\[mtm\] MASK'.
Control: TABLE lines present AND >=1 MASK line; otherwise the instrument/route failed - fix before concluding.
Hypotheses: H1 bit1 set every mission by periodic setter (benign); H2 bit1 is fail/win event, the real mission end needs bit id>=2 whose setter is gated by a never-met condition; H3 table maps ids to other handlers.
Outcome: which bits ever set + fn per id; then grep stores to -0x3620 (funcs_11/30/32/33/35/36/37) for the missing bit's setter and its guard; name the writer (iron rule 11).
HYPOTHESIS-ID: g1-nonhealth-fail
Static result s5753: id-2 bit setter = setHudEnableBit4; next find its callers+guards (grep setHudEnableBit4). Verify soak log captures stderr (s5751 log had 0 [mtm] lines).
