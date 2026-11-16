# NEXT (s7453)
HYPOTHESIS-ID: harness-death-as-void

First: fold SOAK-RESULTS for s7452_fatal_harness (re-queue after the s7452 fix of m6_god_common.sh:94, where a `#` comment
swallowed `| tee $OUT/summary` since s7450). Pass = rc=0, arm P summary `died_in_verify=1 ... crashlines>=1 exitrc=1`,
arm C summary present with alive_at_end=1 crashlines=0. If C still has no summary, look at m6_god_common.sh lines 85-97.
Also consider re-queuing s7449_argck_levels (its rc=1 is suspect for the same reason).

Class DI (offline, one pass): 46 scripts under scratch/agent + tools carry their own fail()/retry copies
(grep -rlE 'died_in_verify|fail (nomission|notitle|nohangar)' scratch/agent tools, excluding soak_queue/done).
Step 1: classify each: (L) live = referenced by a soak_queue recipe or another live harness in the last 300 sessions,
(D) dead copy. For each live one: does a death after its mission/flight gate (a) end the run with exit status + fatal
score, (b) retry silently, (c) not checked. ALSO grep every live harness for the s7452 defect shape: a `#` before a
`| tee`/`>` on the same line (`grep -nE '#[^"]*\| *tee|#[^"]*> *\$'`).
Step 2: members = live (b)/(c). Fix by routing through m6_god_common.sh or the same terminal + exitrc edit;
control = /tmp/s7451fake fake-binary method (BUILD=<dir with a fake RogueSquadron64Recomp>): die-after-gate must give a
terminal line exitrc=1 crashlines=1, live run must give a summary file.
Hypotheses: H-none, H-few, H-many. Discriminator: count of live (b)+(c).
