# NEXT: guest NOBLOCK busy-poll audit (cooperative-scheduler livelock class)
HYPOTHESIS-ID: coop-sched-busy-poll-class
Context: s7195 closed the guard-refusal class (BLOCK recv on a refused mq now parks; old path froze 3/3 with recv_other=0,
i.e. one spinning guest thread starves every other one on ultramodern's cooperative scheduler). The same starvation shape
can arise WITHOUT any refusal: a guest loop that polls osRecvMesg/osSendMesg with OS_MESG_NOBLOCK (or spins on a RAM flag)
until another GAME thread acts. On hardware an interrupt/preemption lets the producer run; here only a blocking call or
check_running_queue yields, and a NOBLOCK recv only drains external (host) messages, never runs another guest thread.
Unit (offline first, s282-s288 class-audit model):
 1. Enumerate every osRecvMesg (53 sites) / osSendMesg (44) / osJamMesg call site in ../N64Recomp/RecompiledFuncs/*.c (10 files) whose a2 (ctx->r6)
    is 0 (NOBLOCK). For each one, read the surrounding loop: does the loop exit on -1 (drain loop: SAFE), or retry until 0?
 2. For each retry-until-0 site, name the producer: host/external (VI, SP, DP, AI, SI, timer -> SAFE, drained inside
    osRecvMesg) or another guest thread (-> LIVELOCK candidate unless the loop also makes a blocking call).
 3. Also grep for guest spin-waits on RAM flags without any OS call in the loop body (e.g. the 0x8011A8C8 / 0x80037808
    vflag waits named in s7193); classify the same way.
 4. Each LIVELOCK candidate: forced arm that makes the producer late (like ROGUESQ_CF0_DELAY_TEST), old path vs a fix
    (yield in the NOBLOCK-fail path, e.g. check_running_queue / a host yield), same-run control.
Hypotheses: H-none (all NOBLOCK sites are drain loops or host-fed) vs H-poll (a guest-produced NOBLOCK poll exists; it is a
second boot-freeze candidate: a spinner would show in [stall-wait] as a thread with huge blocking_calls/last op, not IN).
Discriminator: the table. If H-none, close the class in CURRENT-TRUTH and take the next ladder rung (item 3c).
