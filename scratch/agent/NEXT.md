# NEXT work unit — capture selector producer/context on real audio

HYPOTHESIS-ID: m5-selector-producer-context

Session 3518 resolved the route gate: independent retail controls passed; the
real image arm reached title and hangar, while the silent arm crashed pre-title
at `fillSampleStreamRange` (`0x8000B650`). Use the real image arm next.

The single work unit is one bounded producer/context capture. First ask ground
truth for a newly chosen retail producer range, with whole-RDRAM, selector-span,
and title/hangar controls. Then run one real-audio port capture with
`ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1` and the existing selector-store
control. Build before the run; use `PROBE_PHASE_WIDTH=1024` and
`PROBE_KEYS_FROM_PHASE=1`. Do not use the silent arm or repeat the blocked
VI-640 schedule.

Competing hypotheses:

- `H-ContextProducerParity`: producer context matches retail; divergence is
  later in the path.
- `H-ContextProducerDivergence`: the producer supplies a differing field,
  selecting that producer edge.
- `H-LaterContextMutation`: producer context matches, but a later guest write
  changes the selector writer input.
- `H-CaptureInvalid`: an independent control or target phase is absent.

The discriminator is the first phase-matched difference between retail
producer/context rows and port producer/context plus selector-store rows:
matching producer fields with a differing store selects later mutation; a
first differing producer field selects its upstream edge; failed controls make
the capture unevaluable.
