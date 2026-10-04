# Next work unit: requalify the M5 audio route with a new arm permutation

HYPOTHESIS-ID: m5-route-requalification

Run exactly one new same-build capture with launch order
`declared-real,legacy-real,declared-silent` and a four-second gap, plus the
independent retail oracle. Do not run the `0x800052C4` writer census until the
route result qualifies it.

Competing hypotheses:

- H1: this permutation qualifies all three port arms through title VI 1024 and
  hangar VI 512; the route is ready for the parked writer census.
- H2: at least one arm reaches both target phases but another fails pre-target;
  launch schedule remains the discriminator and writer nulls stay blocked.
- H3: no port arm reaches both target phases despite retail controls; route
  qualification needs a new idea rather than another source census.

Discriminator: retail whole-RDRAM positive control, retail title/hangar VI
controls, and per-arm RSP/audio-stage controls in one capture. Select H1 only
if all three port arms reach both target phases without crash/abort; H2 if at
least one qualifies and another fails; H3 if none qualifies or a required
positive control is absent.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env RS64_BOUNDARY_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4045_m5_route_requal_$(date +%Y%m%d-%H%M%S) RS64_LAUNCH_ORDER=declared-real,legacy-real,declared-silent RS64_LAUNCH_GAP_SEC=4 zsh scratch/agent/run_s4028_m5_route_requal.sh
```

The wrapper must write captures under a non-hidden final path and kill all
children with SIGKILL. Record controls and phase outcomes per arm.
