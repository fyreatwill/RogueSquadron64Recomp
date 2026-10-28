# NEXT: name the writer of the wild 0x38000000 link when arena DL chunks are popped (head11 faults at px1)
HYPOTHESIS-ID: g1c-dd-phase2
Facts (s6565): tail-append (+2944, head unchanged) is fault-free at px1 but pool never emptied (min len 77) so nothing popped. Head-prepend of only +384 chunks (k=1.1, MB=1, head=0x80F18AF8) faults: NULL-node SIGBUS si_addr=0x380000004 in 4/4 attempts.
Hypotheses:
- H-W1: DL words written over the chunk's +0 link (the game writes >0x100 B into a chunk, harmless in the contiguous low pool because the next chunk is simply overwritten link-first, but here something else relies on it).
- H-W2: a DL/RSP-side reader or host mirror masks addresses to 8 MB (0x7FFFFF) so arena chunks alias low RAM and get clobbered / read wrong.
- H-W3: an uninitialised field in my chunks (only +0/+4 set; original chunks identical per relink loop 0x80018044-0x80018054, so unlikely).
Discriminator (one build/run, scratch/agent/s6553_run.sh 6 1 "ROGUESQ_DD_REINITX=1.1 ROGUESQ_DLPOOLX_MB=1 ROGUESQ_CHUNKCUT=1" watch): add a write-watch (rs64 store hook or lldb watchpoint) on +0 of the first 8 arena chunks after [reinitx]; log PC + value of every write. Value 0x38xxxxxx written by a DL-emit PC => H-W1; writes appear at a low aliased address (arena & 0x7FFFFF) => H-W2; no foreign writes yet fault => look at the reader. Positive control: the watch fires on the chunk's own pop (+0 rewritten by the allocator).
Then: if fixable, retest tail/head at px2 x3 for the H-D2 verdict.
