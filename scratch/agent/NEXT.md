# NEXT: who owns 0x80179510 — rs_malloc overlap with the audio pool
HYPOTHESIS-ID: m5-audio-destub
Context: s4555 named the +5436 writer (0x8001E2C0, initTextureLUTAndAllocBuffers clear loop, 36-byte entries) overlapping audio pool nodes at 0x80179510.
Hypotheses: H-A audio pool sits in memory the game later frees, then re-mallocs; H-B rs_malloc/free-list state is corrupt (port-side) and returns an in-use block; H-C retail does the same and only the port timing breaks the walk.
Discriminator (one build, one run): log every rs_malloc (0x80001ACC) / rs_free range (ROGUESQ_LOG_S4429_HEAP at main.cpp:4690 exists; check what it logs) in the s4555 recipe; find the malloc whose range contains 0x80179510 and the earlier alloc/free of the audio pool block. H-A: a free covers the pool. H-B: overlap with a never-freed live block. H-C: tools/oracle shows retail array does not cover 0x80179510. Control: any malloc return must log.
Recipe: scratch/agent/s4555_list_writer.sh (3 arms, crash reproduces 3/3 at ~2 min).
