# NEXT: who holds the rs_malloc lock queue 0x8010FEE0 when the 7th allocateSongChannelArray (rs_malloc 4352) blocks?
HYPOTHESIS-ID: m5-audio-destub
Context (s4579): mixer is a separate host thread running during every alloc (not the differentiator). Alloc #7 blocks at 0x80001B04 (osRecvMessage a0=0x8010FEE0 a1=0 a2=1, BLOCK) - no rs-malloc exit line. Some thread holds the allocator mutex and never sends it back.
Hypotheses:
 H-holder-blocked: another thread is inside rs_malloc/rs_free (took the lock) and itself blocked on something (DMA/audio/event) - the lock is legitimately held; find that thread's last guest PC and what it waits on.
 H-lost-send: a holder finished but the unlock osSendMessage was lost/dropped by our queue impl (full/empty-mq handling, or a guard/crash-recovery path that skipped the unlock).
 H-skipped-unlock: an early-return/guard path in rs_malloc/rs_free (ours, e.g. a mitigation) exits without the osSendMessage, so the queue stays empty.
Discriminator (ONE build): log every osRecvMessage/osSendMessage on mq 0x8010FEE0 (host tid, guest sp, last-guest-pc, queue validCount after) into a ring dumped when alloc #7 'A' prints and again ~2s later. Control: allocs #1-#6 show matched recv/send pairs. Outcomes: unmatched recv by a still-alive tid -> H-holder-blocked (dump that tid's PC/wait); holder's exit path lacks the send -> H-skipped-unlock (name the PC); send logged but validCount not restored -> H-lost-send (queue impl).
Recipe: copy scratch/agent/s4579_window.sh (arms A/B/C, 200 s).
