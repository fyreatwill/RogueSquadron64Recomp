# Next work unit

HYPOTHESIS-ID: H-alloc-window-sched-switch

s4714: record at 0x8003757C is written by retail game PCs (0x800C59xx, 0x800A9Bxx) => the 6 re-allocs (counts 17,16,15,18,18,32) are retail behaviour (A selected; B refuted).
Next unit: determine why allocateSongChannelArray in that window misbehaves in the port.
Hypotheses: (A) port rs_malloc/heap state differs from retail at those allocs (fragmentation, stale freelist); (B) concurrent audio/sched thread races the realloc window (port thread switching); (C) allocation is fine and the fault is downstream (voice array consumers using the old array).
Discriminator: at each of the 6 allocs log heap free-list head/size before/after and old-array pointer lifetime (existing s4579/s4533/RS_MALLOC logs via scratch/agent/s4711_callers.sh); compare with the retail alloc #1; a changed freelist-invariant violation => A, tid differences => B, no violation => C.
