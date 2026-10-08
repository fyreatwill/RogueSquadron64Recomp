# Next work unit: trace the DL walk to the first desync (s4272)

HYPOTHESIS-ID: m5-audio-destub-sequence

Context (s4271): the garbage SetColorImage words are inline-data-looking words in command position (DL at rdramoff ~0x4C7C68, valid E7/F5/F2 then `2F182C30 C8104240` x3 then data). Log: scratch/agent/soak_results/s4271_cimg/arm1.log (grep s4271-w).

Hypotheses:
- A1: our RT64 gbi walker mis-advances (F5 inline-advance rules, op_consume16 for B4/BF, opcode 0x2F unmapped) so it walks into data the producer laid out correctly.
- A2: the producer (our recompiled/LLE F5 ucode output or game) emits the data mid-stream (retail ucode would skip it with correct advance).
- C: RDRAM DL content differs from retail at that point.

Discriminator (one build, one run): in the gbi dispatch loop (rt64_gbi.cpp runDl) keep a ring of the last 64 (dl offset, w0, handler advance) and dump it at the first ODD cimg; also dump the DL's first command of this run. Control: dump the same ring at a SANE cimg. If the ring shows a handler advancing differently from the retail rule (docs/F5-UCODE-REFERENCE.md table) -> A1; if every step matches the reference and data is still in a command slot -> A2/C, then compare to oracle.
Run: zsh scratch/agent/s4271_cimg.sh as template (env ROGUESQ_S4271=1), SIGKILL ~38 s. lib/ edit => export.sh + commit.
