# NEXT (s7452)
HYPOTHESIS-ID: harness-death-as-void

NOTE: docs/CURRENT-TRUTH.md is 60376 B (>60000) -> Step 0 makes s7452 a MAINTENANCE iteration. Do that first; this
unit then moves to s7453.

First: fold SOAK-RESULTS line for s7451_fatal_harness. Pass = VERDICT rc=0: arm P summary `died_in_verify=1 ...
alive_at_end=0 crashlines>=1 exitrc=1` (plant fires at 110 s, inside the 130 s verify window, now terminal);
arm C alive_at_end=1 crashlines=0 exitrc=held vi_stalls30s=0. If P shows allattempts-failed, the s7451 edit to
scratch/agent/m6_god_common.sh did not take (check the died_in_verify line).

Class DI (offline, one pass): s7451 found m6_god_common.sh retried game deaths after the mission gate as void attempts.
46 scripts under scratch/agent + tools carry their own fail()/retry copies
(grep -rlE 'died_in_verify|fail (nomission|notitle|nohangar)' scratch/agent tools, excluding soak_queue/done).
Step 1: classify each: (L) live = referenced by a soak_queue recipe or another live harness in the last 300 sessions
(git log -S / grep soak_queue/done/*s7[0-4]*), (D) dead copy. For each live one: does a death after its mission/flight
gate (a) end the run with exit status + fatal score, (b) retry silently, (c) not checked.
Step 2: members = live (b)/(c). Fix by routing them through m6_god_common.sh or applying the same terminal + exitrc edit;
control = the /tmp/s7451fake fake-binary method (BUILD=<dir with a fake RogueSquadron64Recomp>): die-after-gate must
give a terminal line with exitrc=1 crashlines=1.
Hypotheses: H-none (every live harness already routes via m6_god_common.sh), H-few, H-many.
Discriminator: count of live (b)+(c).
