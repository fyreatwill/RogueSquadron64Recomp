# NEXT: M6 boot freeze, find the dependency cycle (CURRENT-TRUTH item 1)
HYPOTHESIS-ID: m6-boot-freeze-loop
State (s7192): ROGUESQ_CF0_DELAY_TEST=<k>[:<ms>] (src/main/upstream_compat.cpp Rs64Cf0Delay) holds the CF0 receiver (tid 3,
waitForPostSwapAck) after a recv. The retrace thread then blocks on CF0's full-send list with vflag 1, which is the s6993 pre-state,
and it HEALS 10/10. So the freeze needs tid 3 to block on a second queue whose producer waits on retrace.
Unit (offline first, then ONE forced arm, one build):
 1. Static: the guest waits tid 3 makes between CF0 recvs (waittab: waitForPostSwapAck CF0, submitGfxFrame+0xc70 8011A7E8,
    others?). For each queue, name the producer (guest thread, or host external source SP/DP/VI) and whether it can need the
    retrace thread (tid 0, 8011CD28) to run or to have posted (VI msgs, VI_LOCK pacing, osViSwapBuffer, present thread).
    Tools: grep osSendMesg sites to those mq in RecompiledFuncs, src/main/*.cpp enqueue_external_message* callers.
 2. Forced arm: extend Rs64Cf0Delay with ROGUESQ_CF0_DELAY_TEST=<k>:<ms>:hold7e8, which also withholds delivery to 8011A7E8 for
    the hold (or makes tid 3 do a recv on 8011A7E8 during the hold). Arms: hold7e8 40 ms, plain 40 ms (heals, s7192), ctl k=0.
    5 boots each: env HUNT_OWNER=1 HUNT_ENV="ROGUESQ_STALL_DUMP_VI=300 ROGUESQ_CF0_DELAY_TEST=..." zsh tools/boot_freeze_hunt.sh
    Healthy boots keep only the 200-line tail, so the positive control must come from one full-log boot per arm (see s7192 entry).
Outcomes: H-cycle-7e8: the hold7e8 arm freezes with the s6993 dump (retrace on CF0 fullq, vflag 0, tid 3 IN 8011A7E8), so name the
  gating producer and break the dependency (a NOBLOCK retrace post if CF0 is a doorbell; qualify with the same arm).
  H-other-wait: it heals. The second wait is elsewhere, so take step 1's next queue.
  H-none: step 1 finds no producer with a retrace dependency. Then the freeze is not a pure guest-queue cycle (host present/VI
  thread); look at the host [stall-dump] self-sample on the next real recurrence. Stay passive and pivot to the next ladder rung.
Trap: guest scratch for any private queue must sit below rs64_ram_top (use the guest stack); s7192 v1 at 0x9FF00000 was
refused by mesgqueue_guard and froze 10/10 as an artifact.
