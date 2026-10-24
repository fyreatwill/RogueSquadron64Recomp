# NEXT: G1d step 18 - find the real producer of the NULL-dest 0x1000 DMA (devAddr 0xB01A5E20) at 21:9
HYPOTHESIS-ID: g1d-widescreen
Known (s6125): submitDmaRequestBatch ring producer does NOT enqueue this request in either arm (wide or 4:3 ctl), so the ring is cleared. Request follows 0x1000-byte chunks into scratch 0x80716C40 (ctl 0x80766C40).
Hypotheses: H-heap (caller got NULL from rs_malloc when wide FB shifts heap), H-ptr (caller reads a NULL scratch-pointer global), H-other-producer (a non-batch DMA request function builds the mb 0x80110828 entry).
Build one fixup-scripted diagnostic (tools/fixup_*.py, env-gated): (1) log every rs_malloc return==0 with r31 and requested size; (2) log the caller r31 / function at the point the game queues a request whose dest is 0 (the pi-start-dma callers: find the osSendMesg of mb 0x80110828 writers). Run wide arm once + ctl arm; first NULL alloc or first dest==0 queue with caller names the writer.
Outcomes: NULL rs_malloc => heap exhausted at wide FB, move FB/pools above 0x80800000 or enlarge heap; dest from global => trace that global's writer.
