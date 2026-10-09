# Next work unit (s4434): M5 plan Step 10 qualification - is any nonzero PCM produced in the port title phase?

HYPOTHESIS-ID: m5-pcm-nonzero-source

s4433 closed m5-title-reapply-config (retail also calls reapply at title->hangar).
Hypotheses:
- H-source-zero: audio task output buffer is all zero at the AI submit (0x8008EE84).
- H-source-nonzero-host-lost: nonzero at the AI source, zero/lost at queue_samples/SDL.
- H-silent-by-design: title has no music scheduled yet on this route.
Discriminator: one port run (scratch/agent/s4432_port/run.sh recipe; retry on pre-title death) hashing + nonzero-span of the AI buffer at the osAiSetNextBuffer_recomp shim AND at queue_samples, phase-gated to width 1024 (title); same-run positive control = marked buffer. Oracle arm: retail AI DMA source bytes nonzero in title (tools/oracle). Compare per phase.
