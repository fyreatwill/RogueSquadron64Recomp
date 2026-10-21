# NEXT: [mtmst] follow-up — who requests mission transition / sets the end bit
Task: offline. Read requestMissionTransitionMode (funcs_42.c, pc 0x800FB2B0) and grep its callers (funcs_*.c) — list each caller + the guard condition. Enqueue one soak (s5755_mtmb recipe copied from s5754_mtma, env ROGUESQ_LOG_MTM=1) to get the second run.
Hypotheses: H1 transition requested only on mission start (callers = start path), end path never reached because win condition never true; H2 an end-path caller exists but its guard (objective counters) is never satisfied in godmode; H3 end path requests via a different mask value stored through a non-MEM_W(-0x3620) form.
Discriminator: caller list with guards; a caller whose guard reads objective/enemy counts = the next thing to log.
HYPOTHESIS-ID: g1-nonhealth-fail
