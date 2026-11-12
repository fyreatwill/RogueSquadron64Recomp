# NEXT: runtime hazard, external message to a refused mq is requeued forever (CURRENT-TRUTH item 1)
HYPOTHESIS-ID: refused-mq-requeue
Context: s7192 v1 put a timer's target queue at 0x9FF00000 (above rs64_ram_top). mesgqueue_guard refused osCreateMesgQueue, and
every boot froze at fs~600, 10/10 (ctl 5/5 clean). lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp: do_send returns false on a
refused mq (line ~543), and all three delivery paths (dequeue_external_messages ~l.458, wait_for_external_message ~l.472,
wait_for_external_message_timed ~l.484) requeue when `!sent && requeue_if_blocked`. A message that can never be delivered then
loops forever. The waiting thread spins on it and the batch drain re-enqueues it on every pass.
M6 boot freeze is PASSIVE since s7193 (guest cycle refuted by 120 retrace holds, yield = host std::this_thread::yield).
Hypotheses:
 H-requeue-freeze: the infinite requeue is what froze the v1 boots (spin or starvation of later external messages).
 H-other: v1 froze for another reason (e.g. the delayed receiver never woke because its private recv returned at once and the
   game ran on with a corrupted stack slot). Then the fix changes nothing in the v1 arm.
Unit (one build, three arms):
 1. Add a test hook that restores the v1 scratch address: ROGUESQ_CF0_DELAY_TEST=<k>:<ms>:v1 makes Rs64Cf0Delay use 0x9FF00000.
 2. Fix in mesgqueue.cpp: when do_send failed because mesgqueue_guard refused the mq (or mq->msg), DROP the message and log
    `[mesgqueue-guard] dropped undeliverable external msg mq=..` once per mq, instead of requeueing. Keep requeue for genuinely
    full queues. Gate the old behaviour behind ROGUESQ_REFUSED_REQUEUE=1 for the A/B.
 3. Arms, owner env, 5 boots x 34 s each (scratch/s7192/arms.zsh pattern):
    a) v1 + ROGUESQ_REFUSED_REQUEUE=1 (positive control: must freeze, as in s7192 v1)
    b) v1 + fix (expect heal: recv returns at once, no freeze)
    c) k=0 control + fix (expect clean, fs~1950)
 4. lib/ edit: run ./submodule-patches/export.sh and commit the refreshed patch in the SAME session.
Outcomes: a freezes and b heals -> H-requeue-freeze selected, fix lands default-on. Both freeze -> H-other: read the v1 dump's
[stall-wait] table and do not land the fix as a freeze cure (keep it as hygiene only if it is harmless). a heals -> the
control failed, so re-check the v1 hook before concluding anything.
