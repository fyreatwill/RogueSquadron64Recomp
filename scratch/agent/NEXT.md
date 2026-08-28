# NEXT work unit — new M5 route repair or independent handoff edge

HYPOTHESIS-ID: m5-route-repair-handoff

## Competing hypotheses and discriminator

- H-route-producer-missing: the port lacks a producer or handoff needed to
  leave VI 640, while the retail oracle reaches title and hangar.
- H-input/driver-invalid: the validated input or autopilot contract is not
  being delivered in the current recipe.
- H-audio-route-causal: the selected audio arm changes the route before VI
  640; silent and image arms should diverge under a valid same-build capture.

The discriminator is one new route-edge measurement, grounded by the retail
whole-RDRAM positive control, that records the named producer/handoff and
phase transitions for both audio arms in one build. A valid input control with
matching pre-title dispatch but no producer or target phase selects the
missing-handoff direction; a producer with no transition selects its
consumer/ordering contract; an arm-only divergence selects the audio-route
hypothesis. A null without the positive control or valid input delivery is
unevaluable.

## Exact commands

First inspect the already available route producer and handoff anchors, then
add one regeneration-safe or host-side probe only if the measurement is
capable of distinguishing the hypotheses:

    rg -n -C 12 'bufferArbiterProducerMark|8001BCE4|route.*handoff|VI 640|0066A500' src tools scratch/agent
    cmake --build build --config Debug --target RogueSquadron64Recomp -- -j2

Run one same-build paired capture with the retail oracle whole-RDRAM control,
the documented autopilot, and title/hangar phase gates. Do not repeat the
s3028 full-log polling recipe; use a monotonic timestamp or bounded
phase-file checks so the watchdog wall-time is real.

## Constraints

Do not modify audio gates, wait caps, voice guards, AI shims, or writeback
behavior. The M5 Step-1 image/silent comparison remains unevaluable until a
port arm reaches title or hangar. Preserve the dispatch positive control and
record the exact producer PC/value/order if it fires.
