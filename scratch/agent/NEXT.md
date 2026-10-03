# Next work unit: M5 silent-control pre-target stability qualification

HYPOTHESIS-ID: m5-step1-silent-qualification

The s3760 image arm reached title and hangar in the concurrent run and again
image-only on the same build, with positive task/DMA/PCM activity. The silent
arm crashed before target at `spTaskSchedulerThread+9556`. Do not add another
task-data value field or change an audio gate.

Competing hypotheses:

- `H-M5-SilentRouteCrash`: the silent `Broke` control has a repeatable
  pre-target scheduler crash; a same-run silent crash with valid image and
  oracle controls selects this.
- `H-M5-PairPerturbation`: concurrency perturbs the silent arm; both arms can
  reach target when run in the same-build recipe with the image arm removed
  from the failure path. A silent target in a paired run refutes this.
- `H-M5-RunInstability`: the crash is nondeterministic and neither arm is
  reliably target-qualified; inconsistent crash PCs/phases across a repeated
  same-build run leave the explanation unresolved and call for a new
  discriminator.

Discriminator: the oracle whole-RDRAM positive control plus one same-build
concurrent image/silent run, retaining all Step 1 task/DMA/service/slot/
voice/MORT/PCM logs and phase gates. Silent title and hangar rows with a valid
image arm refute pair perturbation and qualify the complete A/B contract.
Another silent pre-target crash at the scheduler boundary, with image and
oracle controls valid, selects the silent-route hypothesis. A changed crash
boundary or missing controls selects run instability.

Before any run, write these hypotheses and the discriminator into this file.
Then build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from the repo root:

`zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh
s3761_m5_step1_silent_qualification`

Use the existing LLE-solo, spin-yield, autopilot,
`PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, oracle positive-control,
and SIGKILL cleanup recipe. Report both arms' phase/crash markers and the
positive-control status before interpreting any null.
