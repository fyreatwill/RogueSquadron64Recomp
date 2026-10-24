# NEXT: G1d step 20 - who consumes the extra ~2 MB of MAIN heap in 21:9, and why is the main heap end 0x8071B670 (vs ctl 0x80795BF0)?
HYPOTHESIS-ID: g1d-widescreen
Known (s6127): NULL = main heap exhausted (free 0xCB0), secondary heap slot 0x8010FF00 zero at that moment; ctl has ~2.6 MB free.
Hypotheses: H-fbpool (wide framebuffer/terrain pools alloc more), H-divert (s6086 bigarena changes heap end/usage), H-order (secondary heap cleared before alloc).
Build/run: env ROGUESQ_G1B=1 XENV_EXTRA="ROGUESQ_ASPECT=21:9 ROGUESQ_LOG_DMA=1 ROGUESQ_HEAPLOG=1 " HOLD_S=30 LEVEL=1 TAG_SUFFIX=<t> zsh scratch/agent/g1_level_coverage_common.zsh ; ctl without ASPECT. Log every rs_malloc >=0x10000 with ordinal in both arms and diff; also log main heap end sentinel after initMainHeap.
Outcome: extra big allocs named -> shrink or move them above 0x80800000; else heap end shift -> fix init size.
