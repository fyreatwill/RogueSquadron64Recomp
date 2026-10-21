# NEXT: fold s5748_mtma/mtmb SOAK-RESULTS logs
grep '\[mtm\]' scratch/agent/soak_results/s5748_mtm*.log. Control: any [mtm] line. Find a0=2 call: ra -> caller (map with funcs grep), b6D/b64/b65/b7 state.
H1 bool 0x6D arm (b6D=1), H2 other arg-2 caller (ra not in checkComplexObjectives/setHudEnableBit4), H3 bool 7 arm (b7=1 in arm a only; arm b should differ).
HYPOTHESIS-ID: g1-nonhealth-fail
