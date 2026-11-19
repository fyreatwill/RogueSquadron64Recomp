# NEXT (s7637)
HYPOTHESIS-ID: generated-symbol-renaming-sweep

G6a/G6b/G6c still wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports on any of them, take that first.
Item 25 closed s7636 (H-mem): bridge walker per-tri cost is memory traffic, no more arithmetic fast paths.
Otherwise take ladder item 4, the generated-symbol renaming sweep. First run
`grep -n '^## Session ' PORTING-STATE.md | tail -15`: if all 15 are sweep sessions, do the REVISIT instead.
Note the churn counter: a rename mapping edit alone reads as no engineering change. Pair each sweep step with a landed tool
change (e.g. a checker that verifies renamed symbols still resolve after regen), or pick an open G-item the owner left.
Hypotheses for the sweep step: H-callers (a func_0x... is named by what its unique caller passes it) vs H-data (named by the
guest table/structure it touches); discriminate by reading the callee body + caller arguments before naming.
Never launch under lldb; never touch build/saves; one game at a time; SIGKILL only.
