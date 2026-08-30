# Session 3266 — retail VI request-state read watch

Date: 2026-08-29
HYPOTHESIS-ID: vi640-request-state-read-edge

## Measurement

Ran the retail oracle twice as one bounded unit. The initial 180-second run
used generic watch output; the fixed 60-second run added `--detail-watch 1`
and `--detail-watch 2` for the selector and pending-state watches. Both arms
used Rice, the documented Start schedule, `--watch-write 0x0:0x800000`,
`--vi-trace`, and watched `applyPendingViChanges` (`0x8001B7F0`), its
mode-application edge (`0x8001B8DC`), and `0x800352D0`.

## Evidence

The fixed run passed the whole-RDRAM positive control with 10,000 writes,
reached title 1024 at origins `0x00790400/0x00790800`, then hangar 512 at
`0x006AB400/0x006AB800`, and exited cleanly at 60 seconds. It observed 3,452
`applyPendingViChanges` executions, 141 executions at `0x8001B8DC`, and 151 at
`0x800352D0`; the predecessor histogram attributes the apply calls to
`0x80019914`.

The pending-state watch `0x00128E94..9C` fired 23,594 reads. Detailed rows
show reads at `0x8001B7F4`, `0x8001B814`, `0x8001B868`, `0x8001B8F0`,
`0x8001B92C`, `0x8001B968`, `0x8001B99C`, `0x8001B9C0`, `0x8001B9E4`, and
related mode helpers; the selector-byte watch `0x00114A865..68` fired zero
reads. The selector null is not a runtime absence: aligned word loads can
cover those bytes without touching the watched byte addresses.

## Result

This proves the pending-state read surface is live in a positive-controlled
retail run, but the current oracle does not print read values or phase labels,
and the selector watch was misaligned for likely word loads. Therefore
`H-RequestState`, `H-BoundaryConsumer`, `H-Phase4SteadyState`, and
`H-ReadWatchUnavailable` remain unresolved; no VI, audio, or mitigation change
is authorized. The next discriminator is one aligned selector-word watch
(`0x00114A864..6C`) with the existing pending watch and detailed rows.
