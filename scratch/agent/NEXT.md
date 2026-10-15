# Next work unit

HYPOTHESIS-ID: m5-retrace-pacing-vs-retail

s4903: gfx task begin R1+0.1 ms, dp_complete R1+20.7 ms (begin->done med 20.6 ms wall), swap +0.1 ms after done => port is 30 Hz because renderer_context->send_dl takes ~20.6 ms > 16.4 ms retrace. H-divider / H-slow-frame-other refuted.

Hypotheses for where the 20.6 ms goes: H-lle-rsp (LLE RSP microcode interpretation, ROGUESQ_LLE_FORCE/UNGATED/SOLO), H-rt64-raster (RT64 RDP raster + Metal work on the calling thread), H-present-wait (blocking on render thread/present/vsync inside send_dl), H-debug-overhead (the logging env vars of the cadence recipe, e.g. ROGUESQ_AUDIO_UCODE / M5_ROUTE_ORDER).
Discriminator: one build, one run: timestamp inside the send_dl path (events.cpp around renderer_context->send_dl; RT64 entry points if cheap) to split LLE-RSP / RDP / present-wait; plus an arm of the SAME recipe with the logging env vars removed (run concurrently, rule 13) to test H-debug-overhead. Positive control: B/D rows stay 1:1 and the full arm reproduces ~20.6 ms.
