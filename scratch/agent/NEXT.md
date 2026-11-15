# NEXT (s7398)
HYPOTHESIS-ID: iomesg-lifecycle

s7397 closed class BG (timer lifecycle): 1 live osSetTimer site, 0 calls on the route, upstream re-arm defect fixed
(ROGUESQ_S7397_TIMERFIX default on). Fold soak s7397_tm_levels (SOAK-RESULTS) first: pass = alive + 0 crash +
tools/s7397_timer_report.py rc 0 on L5/L10/L15.

Work unit, class BH (PI/SI I/O-message lifecycle, next in the message-queue lifecycle family):
1. Static: census every guest osPiStartDma / osEPiStartDma / osPiRawStartDma / osContStartReadData / osEPiReadIo jal site in
   /tmp/s7392.dis (template tools/s7397_timer_census.py: flag librecomp-REPLACED callers): OSIoMesg struct (a0/a1), its
   completion mq, whether the caller receives the completion before the next start with the SAME OSIoMesg (in-loop pattern).
   Read librecomp pi.cpp (osPiStartDma/osEPiStartDma: is the DMA done synchronously, when is the completion message sent,
   does it read the OSIoMesg after the send) for latent defects like s7396/s7397.
2. Hypotheses: H-none (each OSIoMesg is reused only after its completion is received), H-reuse (a struct is restarted while
   its completion is still queued -> wrong msg/size read), H-async (host completion arrives before the guest writes the
   struct fields it later checks).
   Discriminator, ONE build if the code read does not settle it: hook the start calls -> log iomesg, mq, dev addr, size,
   and whether a completion for the same iomesg is still un-received (per-iomesg pending counter decremented in osRecvMesg
   when the received msg == iomesg). Planted control: start one fake DMA twice without a recv (must report 1 reuse).
   Route tools/s7392_mq_run.zsh owner + RETAIL=1 (NOREPORT=1), one at a time. Any lib/ edit: ./submodule-patches/export.sh + commit.
