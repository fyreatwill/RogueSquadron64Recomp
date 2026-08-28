# NEXT work unit — bounded M5 pre-title handoff-edge audit

HYPOTHESIS-ID: m5-route-new-handoff-edge

Audit one genuinely new pre-title producer/signal edge for the VI-640 to
title handoff. Session 3053 positively measured the gfx action path, but the
port still stops at VI 640, so do not repeat action-order, direct-producer,
event-registration, or consumer-only watches.

Competing hypotheses and discriminator:

- H-NewHandoffWrong: the selected edge differs between retail and port before
  title and explains the boundary.
- H-NewHandoffEquivalent: the selected edge matches, so the boundary is
  elsewhere.
- H-EdgeAbsent: the selected edge is absent in one runtime, with positive
  controls proving the watch is live.
- H-MeasurementInsufficient: phase or edge controls do not arm.

The single discriminator is one retail/port table for the chosen new edge,
keyed by VI phase and caller/order, with whole-RDRAM and phase positive
controls. A differing edge selects NewHandoffWrong; matching rows select
NewHandoffEquivalent; a live control with a missing edge selects EdgeAbsent;
an unarmed control selects Insufficient.

Before building, identify the new edge from the existing route call graph and
write its exact retail PC watch and port hook here. Then build one batched
instrument, run retail and port concurrently, and capture bounded phase-keyed
rows from `build/` with SIGKILL cleanup.
