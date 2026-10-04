# Next work unit: requalify the M5 audio route with a new arm permutation

HYPOTHESIS-ID: m5-route-requalification

Competing hypotheses:

- H1: changing the arm permutation to legacy-real, declared-real,
  declared-silent with a one-second gap qualifies all three arms; the route is
  ready for the `0x800052C4` retail-grounded writer census.
- H2: the permutation still leaves only one or two arms target-qualified;
  launch order/timing remains the discriminator and writer nulls stay blocked.
- H3: no port arm reaches both target phases despite retail controls; the route
  is unevaluable and requires a new route-level idea.

Discriminator: one build and one concurrent capture containing the independent
retail oracle plus all three port arms. Require the retail whole-RDRAM positive
control, title VI 1024, hangar VI 512, and per-arm RSP/audio-stage controls.
H1 is selected only if every port arm reaches both target phases without
crash/abort. H2 is selected if at least one arm reaches both phases but another
fails pre-target. H3 is selected if no arm reaches both phases or a required
positive control is absent.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_m5_route_requal_next.sh
```

The wrapper must use `run_s4028_m5_route_requal.sh` with
`RS64_LAUNCH_ORDER=legacy-real,declared-real,declared-silent` and
`RS64_LAUNCH_GAP_SEC=1`, and write captures under a non-hidden final path.
Do not run the `0x800052C4` writer census or M3 runtime qualification until
this route result is recorded.
