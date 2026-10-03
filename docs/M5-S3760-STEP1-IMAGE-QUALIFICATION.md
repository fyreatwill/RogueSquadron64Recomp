# M5 s3760 — Step 1 image-arm qualification

Date: 2026-10-02

The Debug target was built once. The existing oracle plus concurrent image and
silent driver passed the retail whole-RDRAM positive control at 10,000
callbacks and reached retail title and hangar. In the port pair, the image
arm reached title and hangar; the silent control crashed before title in
`spTaskSchedulerThread+9556` with `si_addr=0x400128d47`. The image arm emitted
6,604 phase-qualified task/DMA rows, 26,461 image-stage rows, 560 audio-return
rows, and 559 PCM-consumer rows, and had no crash. The pair was stopped with
SIGKILL after the silent arm failed its target gate.

The required image-only follow-up used the same build and controls. It reached
title at 13.3 seconds and hangar at 24.5 seconds, with 665 task/DMA rows,
2,696 image-stage rows, 283 audio-return rows, 72 PCM-source rows, and 287
PCM-consumer rows, without a crash before SIGKILL. This independently rules
out pair-only interference as the cause of image-arm pre-target loss and
qualifies the image task for Step 1 contract interpretation. It does not
qualify a same-run image/silent A/B because the silent arm died pre-target.

Evidence: `scratch/agent/s3760_m5_step1_contract_pair/` and
`scratch/agent/s3760_m5_step1_image_only/`.
