# NEXT (s7394)
HYPOTHESIS-ID: heap-mutex-reseed-window

s7393 closed class BC (osCreateMesgQueue on a live queue: 0 orphans, lost tokens = mutex re-seeds, owner == retail arm).
Its residual opens class BD.

Work unit:
1. Fold s7393_cq_levels from SOAK-RESULTS (scratch/s7393q/report_l{5,10,15}.txt). Pass = alive, report rc 0 (CONTROL PASS,
   no LIVE row). A LIVE row: read the [s7393-ev] line (mq, caller, recv/send LIVE) and name the writer before any change.
2. Class BD: buildHeapFreeList re-seeds the heap mutex 8010FEE0 at validCount 0 (held, ~10/run) from inside rs_malloc ->
   ensureHeapInitialized, so between the re-seed and rs_malloc's own release the mutex has a free token while a critical
   section is still open. Hypotheses: H-none (no other guest thread ever receives 8010FEE0 inside that window), H-race (a
   second thread enters rs_malloc/rs_free in the window -> heap corruption candidate), H-port-timing (only the port's
   scheduling lets a second thread run there). Discriminator, ONE build: in src/main s7393, on a held re-seed of 8010FEE0
   open a window keyed by the creating guest thread id; count every osRecvMesg success on 8010FEE0 by any OTHER thread
   until the creator's next osSendMesg on 8010FEE0 (window close); also the window length in guest calls. Positive control:
   under a CTL env, from a different thread context inject one recv on 8010FEE0 during the first window (must count 1).
   Same route tools/s7392_mq_run.zsh, owner + RETAIL=1 arms. Static half: read buildHeapFreeList's caller chain in
   /tmp/s7392.dis (who calls it with the mutex held) and whether retail can switch threads there (no blocking call
   between re-seed and release = no switch on N64's non-preemptive-at-equal-priority scheduler).
