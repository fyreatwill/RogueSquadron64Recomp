# M5 Session 3524 — selector tick route boundary

The retail oracle used whole-RDRAM writes and the existing `0x80029E78`
execution watch. It reached title 1024 and hangar 512; the watch fired in
hangar from `0x80029E64` with the known retail context.

The corrected real-audio port run restored the existing selector controls after
regeneration. The new `runVideoFrameTick` table had an all-width positive
control and five title rows (`caller`, `advance-return`, and three guards),
but no hangar rows. Producer-context, both selector stores, and mixer entry
remained live in hangar; the known route witness was title-only and the
AI-boundary witness was absent. All four generated direct callers were covered.

This selects a route-path difference at static caller scope: an enclosing
route gate or a non-generated/indirect alternate path reaches the stores
without the known `runVideoFrameTick` path. The next unit traces the immediate
store callers.

ORIGIN: all probes observe phase, PCs, arguments, and branch outcomes. No
audio, selector, task, or output state was rewritten.
