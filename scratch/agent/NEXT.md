# NEXT work unit — qualify the port at the retail producer boundary

HYPOTHESIS-ID: m5-port-producer-boundary

Session 3406 scanned main plus all overlay sections and found 88 direct JAL
sites to `rs_memset`; `0x8002BEEC` is not a direct JAL (`0x42000018`). The
focused oracle arm passed controls and observed `0x8002BEEC` 191,046 times,
with `exec-prev pc=0x800078EC prev=0x8002BEEC n=177`.

Competing hypotheses:

- `H-PortBoundaryPresent`: the port executes `0x8002BEEC` and exposes the same
  producer predecessor relation; the gap is downstream.
- `H-PortBoundaryAbsent`: the port does not execute `0x8002BEEC`; the missing
  producer dispatch remains upstream.
- `H-PortBoundaryDifferent`: the port executes it with a different predecessor
  or route relation, indicating address reuse or overlay divergence.

Discriminator: in one fresh build/run, retain the existing port PCM/image
controls and add phase-qualified execution/predecessor logging at
`0x8002BEEC` and `0x800078EC`. Controls must include the qualified route,
title/hangar VI transitions, audio ABI/DMA, image-stage, and nonzero PCM
boundary controls. Matching execution plus the same predecessor selects
`H-PortBoundaryPresent`; zero execution with controls live selects
`H-PortBoundaryAbsent`; a different predecessor selects
`H-PortBoundaryDifferent`.

Use the existing completion-safe port contract-pair recipe, adding only the
two boundary PCs in its already-batched configuration. Build once, run silent
and image arms concurrently, and SIGKILL both after target phases. Do not alter
waits, slots, dispatch, or PCM writeback.

Evidence: `docs/M5-S3406-RETAIL-PRODUCER-DISPATCH.md`.
