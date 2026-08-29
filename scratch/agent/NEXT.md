# NEXT work unit — ground the upstream route divergence in retail

HYPOTHESIS-ID: m5-audio-route-upstream-boundary

## Single work unit

Use one independent retail-oracle run to enumerate a new phase-gated
writer/consumer handoff immediately before `0x800356AC:0x80035B00`.
Session 3126's port probe had valid controls (VI-context 8 rows and host
voice-audit 1 row), but the port reached only VI 640 and had zero rows from
the retail-live continuation. Audio and route behavior remain out of scope.

## Competing hypotheses

- H-RetailPreConsumerBoundary: a newly watched retail PC immediately before
  the continuation is live in title/hangar and names the next port boundary.
- H-RetailBoundaryAbsent: the proposed pre-consumer handoff is not
  target-phase live; choose a different statically identified handoff.
- H-RetailControlInvalid: the whole-RDRAM positive control or title/hangar
  phase markers fail, so the oracle result is unevaluable.

## Discriminating measurement

In one bounded retail-oracle run, the whole-RDRAM control must fire and retail
must reach title 1024 and hangar 512. A target-phase row from a newly named
pre-consumer PC selects H-RetailPreConsumerBoundary; no row with valid
controls rejects that candidate; a missing control or phase marker selects
H-RetailControlInvalid.

## Exact commands

1. Use the retail oracle's whole-RDRAM positive control and one newly selected
   pre-consumer execution watch, phase-gated to title/hangar VI transitions.
2. Run once with the fixed oracle recipe, capture the full log, and kill with
   SIGKILL if the watchdog expires.
3. Record the control, title/hangar phases, watched PC rows, and selected
   hypothesis; do not add a port instrument until the writer/consumer PC is
   named.
