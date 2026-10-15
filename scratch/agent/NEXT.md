# Next work unit

HYPOTHESIS-ID: m5-retrace-pacing-vs-retail

s4905: fullSync 11 ms/frame = fsRender 5.2 (renderToRDRAM fb-pair loop) + fsTail 3.5 (post-advanceWorkload, present-early) + fsEvict 1.9. GPU waits ~0, upload ~0.
Open: which sub-part dominates each bucket (per fb-pair encode vs texture load; present-early block; textureCache->evict). Resolution test unqualified (no control).
Decision: 30 Hz is host-bound (>16.4 ms). Either one more batched split (add S4267Seg marks inside the 2682 render loop and around evict/present-early; one build, one run) or park and resume the M5 audio de-stub plan (docs/M5-AUDIO-PLAN.md) — recommended: ONE final split, then park regardless of result.
