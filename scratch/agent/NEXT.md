# NEXT: G1d step 17 - read the s6124 ring-producer soaks (wide vs ctl) and name the writer of the NULL DMA dest
HYPOTHESIS-ID: g1d-widescreen
Known (s6124 analysis): 4:3 ctl has 0 dram=0 DMAs; 21:9 has one (ROM 0x1A5E20, mb 0x80110828) right after valid chunks into scratch 0x80716C40 (ctl scratch 0x80766C40).
Read first: SOAK-RESULTS lines s6124_g1d_ring_wide / _ctl; logs in scratch/agent/m6/*s6124_ring_*/ . grep '\[dma-ring-producer\]' near the first `devAddr=0x01A5E20` / dramAddr=0x00000000.
Hypotheses: H-heap (producer enqueues dramAddr=0: caller got NULL from an alloc) ; H-clobber (producer logs valid dramAddr, slot zeroed before consume); H-ptr (caller reads a NULL scratch-pointer global).
Discriminator: producer's dramAddr for that request. 0 => H-heap/H-ptr: then lldb/host-backtrace at the producer (static jal does not keep r31) or add a rebuild-based alloc-failure log (needs fixup script, not live regen). Valid => H-clobber: find who writes ring slot +8.
Fix direction: place wide framebuffers in extra mapped RAM above 0x80800000 if RDP masking allows, or find why heap shrinks; name the writer (rule 11).
