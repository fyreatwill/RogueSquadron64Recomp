# Next work unit (s4324): requalify the real-image filter-path matrix

HYPOTHESIS-ID: m5-step9-mort-output

State (s4323): the independent MORT reference and oracle controls passed, but
both corrected port arms crashed at `rs64_m5_descriptor_start+460` / guest
`0x8000834C` before VI 512. The caller/entry witness produced no rows. The
prior s4322 hangar result remains the route-valid baseline.

Competing hypotheses:

- H-route-state: the current seeded-save/descriptor crash is a route or state
  setup difference, and the prior qualified matrix can be restored.
- H-real-eligibility: real-image descriptors fail an eligibility/status gate
  before the enumerated filter callsites.
- H-real-dispatch: real-image audio takes an alternate filter/decoder dispatch
  path not covered by the three enumerated callsites.

Discriminator: copy the known seeded save into the active build, then run one
batched silent/real matrix with the existing branch witness, MORT reference,
oracle whole-RDRAM, VI title/hangar, filter, and PCM controls. Both VI 512
markers with no descriptor crash refutes H-route-state and permits the branch
comparison. Another pre-512 crash selects H-route-state. A real-arm eligibility
failure selects H-real-eligibility; a real-arm branch to a named alternate
selects H-real-dispatch. A run without both VI 512 markers is invalid.

Before any build, inspect the relevant source and preserve the positive controls:

`rg -n '8009C540|8009C88C|8009D740|filter-voice-audit|init-desc|ROGUESQ_AUDIO_UCODE' src/main RecompiledFuncs scratch/agent/run_s4321_m5_mort_output.sh`

If `build/saves` is not the known seeded 7F baseline, restore that baseline;
then build once with:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the same matrix recipe:

`zsh scratch/agent/run_s4321_m5_mort_output.sh`

Keep `M4_Y8000_WIDTH=512`, reference selection `--indices 0,1,59,90`, and all
existing controls. No decoder, AI bridge, RSP dispatch, or game-path guard
change is authorized.
