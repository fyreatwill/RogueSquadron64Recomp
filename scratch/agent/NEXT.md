# NEXT: G1 - s5850: what increments objective counters 1 and 10, and which of the 21/6 needed are missing?
s5849: invuln run c1 plateaus at 8, c10=0, c2=0 over 723 s hold (m6/s5849i). Win arm needs c1>=21 or c10>=6.
Hypotheses: H1 c1 increments come from specific object-kill classes (autopilot kills 8 of them, then runs out of targets in reach); H2 c1 increments are tied to scripted triggers (waves spawn by position/time) the autopilot never reaches; H3 c10 is a different event (e.g. rescue/escort completion).
Discriminating measurement: one build logging every writer of 0x8013805C+4 and +40 (setter fn, caller via backtrace, id args) with vi; find setter via grep of funcs for stores to 0x8013805C/0x80138060 region (existing getObjectiveCount/setObjective fn). Compare setter's callers at the 8 increments vs c10 callers (static: who calls with idx 10).
HYPOTHESIS-ID: g1-mission-progression
