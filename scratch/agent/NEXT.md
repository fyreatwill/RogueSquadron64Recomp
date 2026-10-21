# NEXT: G1 — who calls datItemSetObjectiveBooleanCount(0,0,2) and why it increments mission-fail counter 2
Evidence (s5790 fire arm): each counter-2 rise is preceded by datItemSetObjectiveBooleanCount a2=2 a0=a1=0. Read funcs_15.c:4148 body; add host backtrace on a2==2 (first 6) via a patch extension; compare nofire arm (queued) to see whether rises occur without fire input.
Outcomes: caller named (script/dat trigger) -> read its condition; if it is a legit trigger the "fail" semantics of counter 2 are misunderstood -> check what threshold the game compares counter 2 against.
HYPOTHESIS-ID: g1-mission-progression
