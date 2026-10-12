# NEXT: validate per-DMA overlay registration on the boot/route path
HYPOTHESIS-ID: overlay-dispatch-per-dma

Competing hypotheses and discriminator for this iteration:

- H1: the current chunk-start registration is sufficient; the overlay is
  registered before its first call and the route change is not needed.
- H2: some overlay DMA is wholly contained in a section and is missed by the
  chunk-start-only helper; registering with the canonical full-range helper on
  every ROM DMA makes the menu/cinematic dispatch path available.
- H3: registration is not the route blocker; the runtime build will compile,
  but the new helper call will produce no matching section and cannot alter
  dispatch.

The discriminating change is to invoke both the canonical `load_overlays`
full-range matcher and the existing chunk-start matcher after each ROM DMA.
Build success plus overlay-match logs/route behavior distinguish H1/H2/H3;
the full-range call is a no-op for partial asset DMAs.

Run the rebuilt port from `build/` with `ROGUESQ_LOG_DMA=1` and the existing
phase controls. Check whether the new canonical matcher logs menu/cinematic
sections and whether the port reaches the known title/hangar VI origins. Keep
the existing independent oracle schedule for route comparison; do not add a
new diagnostic field.

Expected discriminator:

- H1: menu/cinematic overlay match rows appear and the route advances beyond
  the prior clear-only behavior.
- H2: only chunk-start rows appear; the canonical matcher is a no-op on the
  covered route, leaving the route unchanged.
- H3: matcher rows appear but VI progression remains unchanged, selecting a
  downstream route blocker.
