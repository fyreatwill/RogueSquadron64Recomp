# Next work unit (s4432): why is the port's title audio loop (0x8008EE10..0x8008EE9C) not calling osAiSetNextBuffer at 0x8008EE84?

HYPOTHESIS-ID: m5-audio-loop-submit

s4431 (static): 0x80029E78 = osAiSetFrequency epilogue; 0x80029E80 = osAiSetNextBuffer entry. Retail title calls the latter from 0x8008EE84 (a1=0x300); port does not.
Hypotheses:
- H-loop-not-run: port never executes the loop (audio thread not scheduled / gated upstream).
- H-branch-skip: loop runs but the branch at 0x8008EE98 (beq on byte@0x801596F0 & 0xFF) skips the submit; state byte differs.
- H-shim-bypass: osAiSetNextBuffer is routed via a shim so a PC witness at 0x80029E80 never fires (instrument gap).
Discriminator: ONE port run, counters at 0x8008EE10 (loop head), 0x8008EE84, osAiSetNextBuffer_recomp entry, and the byte at 0x801596F0, phase-gated on title VI. Positive control: reapplyAudioConfig entry witness (known to fire). Paired retail run via tools/oracle with the same PCs. Recipe base: scratch/agent/s4429_port/run.sh (ROGUESQ_LOG_ALL=1).
