# NEXT (s7546)
HYPOTHESIS-ID: class-gf-host-reads-destroyed-thread

Class GE is CLOSED (static s7544 + runtime s7545 score 0). s7545 v1 (no destroy tracking) showed the guest reuses a destroyed
thread's OSThread struct within ~2 s (0x80193050 destroyed t=4.9, MusyX voice render writes it at 6.8, incl. +0x20 where the port
keeps its host UltraThreadContext* and +0x28 sp). So the port must never read a destroyed thread's struct afterwards.

Work unit: class GF static census (tools/s7546_gf_census.py, --controls), then a runtime witness only if a row is OPEN.
- Enumerate every ultramodern/librecomp host read of an OSThread field: `TO_PTR(OSThread, ...)->`, `OSThread* x = TO_PTR(...)` then
  `x->next/priority/queue/state/flags/id/context/sp` (threads.cpp, scheduling.cpp, threadqueue.cpp, mesgqueue.cpp, ultra_translation).
- Classify each read: H-live (the thread is the caller itself and running, or is in a queue/run list = not destroyed), H-after-destroy
  (reachable after osDestroyThread(other) for that thread: e.g. wait_for_resumed threads.cpp:289 reads this_thread()->context
  when a destroyed thread wakes; thread_queue_remove on a stale queue pointer), H-dead (unreachable in this game).
- For each H-after-destroy row: what value the guest can have written there (s7545 v1 log scratch/s7545_thrwatch_v1/log_l1.txt has
  real reuse values) and whether the read then derefs it as a host pointer (crash) or only compares it (benign).
- Controls: planted read of a destroyed-thread field in a fake function -> OPEN; deleted rule -> unclassified.
Hypotheses: H-safe (every post-destroy read only compares, e.g. context != mine -> self-destroy), H-deref (some path derefs
t->context of a reused struct -> fix: keep context host-side in a map keyed by t_, =0 knob), H-none (no post-destroy reads).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
