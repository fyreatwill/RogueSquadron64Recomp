# Next work unit: locate the M5 image source-span producer

HYPOTHESIS-ID: m5-image-preimage-producer

Competing hypotheses and discriminator written before the next build:

- H-guest-producer: a legitimate guest store writes the port source span with
  zero values before the image task reads it.
- H-host-producer: a host-side copy/DMA path writes or clears the span after
  the guest producer and before the image task.
- H-producer-absent: no qualified writer reaches the span before the image
  task, so the zero source is an upstream missing route/producer.
- H-control-invalid: if retail whole-RDRAM/title/hangar controls or either
  image target phase fails, the corresponding null is unevaluable.

The single discriminating measurement is one same-build, retail-grounded,
phase-gated writer census for the full span, joined to the next image-task
read for declared and legacy arms. Retail ground truth qualified the physical
span (`664` writes; hangar snapshot nonzero=24); the paired port capture
qualified both target VIs and read zero from it in both arms. Classify every
qualified writer as guest store, host copy/DMA, or absent, with writer PC,
value, task generation, and phase. A zero-valued guest writer selects
H-guest-producer; a host write selects H-host-producer; no writer before the
read selects H-producer-absent. Retail whole-RDRAM/title/hangar and both port
image target VIs are mandatory positive controls; a missing phase makes that
arm unevaluable.

ORIGIN: the candidate values are legitimate image source bytes; s4111 showed
the port reads the span directly as zero and did not observe a DMA into
`DMEM 0xCC0`. No skip, force-clear, or guest behavior change is authorized.

Exact work: ask the oracle for the same physical span with the whole-RDRAM
positive control and target phase gates before the next build. Then enable the
existing regeneration-safe guest-store and host-write witnesses together,
rebuild once if needed, and run declared/legacy with the existing
stage/task/PCM controls. Any missing title/hangar gate invalidates that arm.
