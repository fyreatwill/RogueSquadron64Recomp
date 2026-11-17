# NEXT (s7544)
HYPOTHESIS-ID: class-ge-thread-state-fidelity

Fold first: SOAK-RESULTS lines for s7540_rwait_cost (fps NODRAIN=3 vs =1 vs drained, tools/g1e_level_fps.py; needs AC). If it
voids out (SOAK_MAX_VOIDS), rerun in-session with ALLOW_SLOW=1 ALLOW_BATT=1 and score in-run only.

Work unit: class GE census (offline, one tool, the s7542/s7543 model): libultra thread-state fidelity of the runtime replacements.
For every replacement that writes OSThread state / queue / priority or moves a thread between queues (osCreateThread, osStartThread,
osStopThread + osStopThread_recomp, osDestroyThread, osSetThreadPri, osYieldThread_recomp, do_send/do_recv blocking, swap_to_thread,
schedule_running_thread, run_next_thread, _thread_func exit), tabulate (state before -> state after, which queue t->queue names
after) and compare with libultra 2.0 semantics (STOPPED=1 RUNNABLE=2 RUNNING=4 WAITING=8; osStartThread on STOPPED/WAITING,
osStopThread on RUNNING/RUNNABLE/WAITING, ...). Note the port's OSThreadState enum values first (boring check).
Seed row (s7543): osStopThread_recomp(NULL) yields without state=STOPPED. Hypotheses per row: H-equal (same transition), H-benign
(differs but no guest reader of t->state/t->queue: grep RecompiledFuncs for loads at OSThread +0x10 state / +0x8 queue, offsets
from the port's OSThread), H-diverge-OPEN (differs and the game reads it, or a later replacement branches on it, e.g. osStopThread
on a self-stopped thread takes the `t->queue != NULLPTR` path).
Discriminating outcome: 0 H-diverge-OPEN closes GE; a named OPEN row -> next unit: a runtime counter on that transition (one build,
all OPEN rows at once, positive control = force the transition) and then a fix with =0 restoring the old behaviour.
Tool: tools/s7544_ge_census.py --controls (plant a wrong state store -> that row OPEN; delete a rule -> unclassified). Exit 0 only with
0 OPEN / 0 unclassified.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
