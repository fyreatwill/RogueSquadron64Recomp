# NEXT work unit — capture first internal selector-path boundary

HYPOTHESIS-ID: m5-selector-producer-context

Session 3519 resolved the producer/call boundary: independent retail controls
passed; retail and the real image arm agree on `a0=0x80165ED0`, `a1=0x12`, and
the port reached title and hangar. Retail's internal call at `0x80029E78`
observes/returns `0x561F` from input `0x5622`, while the port store context is
`0x5622`. Use the real image arm next.

The single work unit is one bounded internal-boundary capture. First run the
retail oracle with whole-RDRAM and selector-span controls plus
`--watch-pc 0x80029E78` and `--pc-phase-log-width 0x006AB400:512`. Then build
and run one real-audio port capture with a regeneration-safe witness at the
`0x80029E78` entry, the existing selector-store control, and the same
phase-gated route. Use `PROBE_PHASE_WIDTH=1024` and
`PROBE_KEYS_FROM_PHASE=1`; do not use the silent arm or repeat the blocked
VI-640 schedule.

Competing hypotheses:

- `H-ContextProducerParity`: the call inputs at `0x80029E78` match retail.
- `H-ContextProducerDivergence`: the port call input differs from retail,
  selecting the function's upstream producer.
- `H-LaterContextMutation`: call input matches, but its return or a later
  guest write changes the selector writer input.
- `H-CaptureInvalid`: an independent control or target phase is absent.

The discriminator is the first phase-matched difference between retail
producer/context rows and port producer/context plus selector-store rows:
matching producer fields with a differing store selects later mutation; a
first differing producer field selects its upstream edge; failed controls make
the capture unevaluable.
