# NEXT: fold s5728_sup{a,b,c} (SOAK-RESULTS.md). a = baseline, b/c = ROGUESQ_SUPPRESS_BOOL=7.
H1: bool 7 causal for fail arm -> b/c mission_cycles drop vs a (a≈3) and flight outlives ~180 s. H2: not causal -> same cycles (then bool 1/0x63/0x65 or a timer is the fail driver; try SUPPRESS_BOOL=0x64,0x65). H3: suppression breaks mission (crash/stall).
Control: m6/<tag>/run.log has [objbool-sup] lines in b/c, none in a. If b/c never show a sup line, bool 7 is never set in this window -> datum, inspect [objbool] ids.
HYPOTHESIS-ID: g1-bool7-suppress
