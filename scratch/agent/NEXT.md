# Next work unit: clean dummy launch-timing A/B

HYPOTHESIS-ID: m5-dummy-launch-timing

Session 4072 ran only the dummy-silent arm after the retail oracle positive
control. Retail reached title 1024 and hangar 512, and clean dummy-only also
reached both gates without a crash or abort. This supports Hnative-residue over
a deterministic dummy-start dependency, but session 4069's native-first dummy
crash and session 4071's native-first success leave timing/resource sensitivity
open.

Competing hypotheses:

- Hlaunch-timing: an immediate clean dummy launch fails while a fixed delayed
  launch succeeds, proving startup timing is the discriminator.
- Hdelayed-resource: immediate clean dummy succeeds while the delayed arm
  fails, proving delayed resource interaction rather than native residue.
- Hresidue: both clean dummy arms succeed, strengthening the native-predecessor
  residue explanation.
- Hcontrol: the retail positive control or either phase gate fails; no route
  conclusion is valid.

Discriminating measurement: one same-build capture with two clean
dummy-silent processes after the retail positive-control marker, one launched
immediately and one after exactly 7 seconds. Keep `ROGUESQ_AUDIO_UCODE=0`, the
LLE/spin-yield settings, scheduler breadcrumbs, both phase gates, and SIGKILL
cleanup. Immediate-only failure selects Hlaunch-timing; delayed-only failure
selects Hdelayed-resource; two successes strengthen Hresidue; a missing
control or phase gate selects Hcontrol.

Exact implementation for the next iteration: extend
`scratch/agent/run_s4069_m5_sequential_silent.sh` with a clean dummy-only
`immediate` arm and a clean dummy-only `delayed` arm, using a 7-second sleep
only between the two launches, then run:

`env RS64_SKIP_NATIVE=1 RS64_S4072_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4072_m5_dummy_timing zsh scratch/agent/run_s4069_m5_sequential_silent.sh`

Do not reopen sink qualification unless an arm reaches both phase gates.
