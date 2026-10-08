# Next work unit: what is special about wall time ~28 s in the private-DMEM B arm? (s4255)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4254: VI 640 is the normal 52-56 s intro; the crash (1/6 to ~40%) lands ~28 s inside it at varying sites (fillSampleStreamRange+8516, emitAllocatedDLCommand+16244). Free list intact at crash.
Hypotheses: h1 a timer/audio-thread event near 28 s writes a wild guest pointer; h2 a DL/audio buffer wraps at a fixed frame count; h3 plain host race (private-DMEM audio thread vs main).
Discriminator: A (shared lock) arms vs B arms in one wave (crash rate), plus the faulting pointer's source register chain at the crash across 3+ crashed arms.
Harness: env OUTN=g TAG=_1 ARMS="A1 A2 A3 A4 B1 B2 B3 B4" SECS=75 ROGUESQ_LOG_S4222=1 zsh scratch/agent/s4252_ab.sh ; classify by CRASH + pc-symbol.
