# NEXT work unit — trace an upstream selector-store caller/context edge

HYPOTHESIS-ID: m5-selector-producer-context

Session 3516 qualified the live selector stores and added a port context hook,
but the retail oracle's field-dump mode emitted no comparable register tuple.
Do not repeat `0x8009192C`, which was absent in the hangar phase, or repeat the
completed live-store context capture unchanged.

The next witness is the first live execution/caller edge in the function range
`0x8009189C..0x80091B3C`, which contains the mixer initialization and its
selector-store path. Ask the independent retail oracle first with whole-RDRAM
and selector-store controls plus a phase-gated PC range. Then add one
regeneration-safe port witness at the first live caller/context edge, build
once, and run the validated real-image/LLE/spin-yield/autopilot route with
title and hangar buckets.

Competing hypotheses:

- `H-ContextProducerParity`: the first live upstream context matches; the
  differing value is introduced earlier or by a later mutation.
- `H-ContextProducerDivergence`: the first live upstream context differs in
  `s1` or related fields; that producer edge is selected.
- `H-LaterContextMutation`: upstream context matches, but an intervening guest
  instruction changes it before the store.
- `H-CaptureInvalid`: whole-RDRAM, selector-store, phase, or range controls
  fail, making the join unevaluable.

The discriminator is the first live PC and its phase-matched context joined to
the existing writer PC, store ordinal, and value. Matching upstream context
with a later writer difference selects mutation; the first differing context
field selects producer divergence; failed controls select capture invalidity.

Exact first command shape:
`tools/oracle/build/rs64_oracle ... --watch-write 0x0:0x800000
--watch-write 0x00149758:0x00149760 --watch-pc-range 0x8009189C:0x80091B3C
--pc-phase-log-width 0x006AB400:512 --pc-hist-watch 1 --vi-trace`.
Retain the verified Rice video and Start schedule. The port command must use
`ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1`, `PROBE_PHASE_WIDTH=1024`, and
`PROBE_KEYS_FROM_PHASE=1`; use SIGKILL, a non-dot final capture path, and run
from `build/`.
