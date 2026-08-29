# NEXT work unit — M5 target-phase qualification after route selection

HYPOTHESIS-ID: m5-target-phase-route-boundary

## Single work unit

M5 remains the strategic priority, but the retained `s2618` and eleven-Start
routes both stopped at pre-title VI 640 in the same-build qualification. Do
not repeat either route unchanged. The next unit is one phase-gated audio
qualification pair after a human selects a new route or supplies an equivalent
retail-grounded boundary.

Competing hypotheses and the discriminating measurement:

- `H-AudioPath`: real-audio image-arm execution reaches title/hangar and joins
  DMEM, DMA, SP completion, service, slot, and PCM evidence.
- `H-SilentEquivalent`: real-audio and silent-control arms stop at the same
  phase with dispatch controls but no target-phase audio joins.
- `H-RouteBoundary`: the selected route changes the phase boundary before the
  audio joins, so the prior nulls were unevaluable rather than audio evidence.

The discriminator is the same-build, phase-gated pair with
`ROGUESQ_AUDIO_UCODE=0/1`, `ROGUESQ_LOG_ALL=1`, and positive dispatch controls;
the first divergent VI phase plus the joined audio counters selects among the
hypotheses. Image-arm DMEM/DMA/SP/service/slot/PCM joins are required before
any audio conclusion.

Exact command is the retained M5 contract-pair recipe in
`docs/M5-AUDIO-PLAN.md`, with the newly selected route substituted. Run from
`build/`, capture each arm, and terminate with SIGKILL if the watchdog fires.
Do not build or run until the route changes.
