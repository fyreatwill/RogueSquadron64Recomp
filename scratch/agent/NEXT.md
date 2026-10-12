# NEXT: qualify both overlay matcher arms with same-run controls
HYPOTHESIS-ID: overlay-dispatch-per-dma

Competing hypotheses and discriminator for the next iteration:

- H1: the full-range matcher is being called and can match a complete overlay
  section; its missing rows in s4672 were an instrumentation blind spot.
- H2: the covered overlay transfers are chunked, so only the start matcher can
  match them and the canonical call is a harmless no-op.
- H3: a full-range match occurs but overlay dispatch is not the route blocker;
  the route still fails independently in the audio/VI path.

Add one batched counter/log pair in the overlay runtime: count every call and
every section match for `load_overlays` and `load_overlays_by_start`, with a
whole-DMA positive control in the same run. Build once, then run the canonical
route for 100 seconds with `ROGUESQ_LOG_DMA=1` and `ROGUESQ_LOG_PHASE=1`.
Do not use a null from either matcher unless its positive control fires.

Run from `build/` with the existing real-audio/LLE/ungated/solo/spin-yield
configuration and phase controls. Check both matcher call/match counts and
whether the port reaches the known title/hangar VI origins. Keep the
independent oracle schedule for route comparison.

Expected discriminator:

- H1: full-range positive control and a real full-section match both fire.
- H2: full-range positive control fires but has no overlay matches, while the
  start matcher matches the chunked sections.
- H3: a full-range match fires and VI progression still fails before the
  qualified 512 origin, selecting a downstream blocker.
