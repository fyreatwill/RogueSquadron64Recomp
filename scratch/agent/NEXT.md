# Next work unit (s4322): requalify the M5 Step 9 hangar route

HYPOTHESIS-ID: m5-step9-mort-output

State (s4321): the independent MORT reference decoder passed four descriptors
covering both 8000 and 16000 Hz with nonzero decoded output. The oracle whole-
RDRAM/title controls passed. Both port arms reached title VI 1024 and had PCM
source/consumer rows, but neither reached hangar VI 512; the runtime filter
edge therefore produced zero rows and the MORT/layout/AI discriminator did not
run. This is a route-invalid null.

Competing hypotheses:

- H-MORT: once VI 512 is reached, the active descriptor/filter rows and their
  nonzero PCM output will match the independent MORT reference class.
- H-layout: VI 512 is reachable but descriptor fields/type/rate do not map to
  the reference rows, producing filter rows without matching output.
- H-AI: VI 512 and valid nonzero CPU output will appear, but the AI/host PCM
  join will diverge.

Discriminator: one build/run with the MORT reference rows, oracle positive
control, title and hangar phase controls, and both port audio arms. The run is
valid only if both arms reach VI 512 at origin `0x006AB400` and the active
filter callsite emits rows. Matching descriptor type/rate plus ordered nonzero
PCM selects H-MORT; a type/rate mismatch with valid filter rows selects
H-layout; matching CPU output with a missing source/consumer join selects
H-AI. If VI 512 is absent again, record the route as invalid and pivot to the
route discriminator; do not infer a MORT null.

Before building, verify the known route recipe and retain the positive controls:

`rg -n 'ROGUESQ_AUTOPILOT|PROBE_PHASE_WIDTH|M4_Y8000_WIDTH|filter-voice-audit|pcm-boundary' scratch/agent/run_s4320_m5_callsite_trace.sh scratch/agent/run_s4321_m5_mort_output.sh src/main docs/CURRENT-TRUTH.md`

Then update `run_s4321_m5_mort_output.sh` only if the route recipe needs the
known `M4_Y8000_WIDTH=512` qualifier, build once with:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

and run:

`zsh scratch/agent/run_s4321_m5_mort_output.sh`

Keep the reference selection `--indices 0,1,59,90`; it covers both global
sample-rate classes. No decoder, AI bridge, RSP dispatch, or game-path guard
change is authorized.
