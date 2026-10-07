# Next work unit: validate the M5 drain-tick policy A/B

HYPOTHESIS-ID: m5-drain-tick-policy-validation

Run the existing three-arm validation recipe `scratch/agent/run_s2328_m5_drain_tick_ab.sh` after the key-on audit closed with no guard hits. This is one bounded validation unit: keep the image arm's default-off drain tick and compare it with the same-build `ROGUESQ_DRAIN_INLOOP_TICK=1` control; retain the silent stub as the task-dispatch control. Do not change the policy.

Competing hypotheses:

- Hdrain-required: tick-on is required for a qualified hangar route or for downstream task/SP, slot/status, or PCM joins; tick-off loses one of those controls.
- Hdrain-redundant: both image arms qualify with matching downstream joins and tick-on only adds redundant tick rows.
- Hdrain-coverage: one or both image arms lack the whole-RDRAM oracle control, phase gate, or shared positive controls, so the comparison is unevaluable.

Discriminating measurement: the oracle must pass its whole-RDRAM and retail title/hangar controls. Both image arms must reach port hangar `512 @ 0x006AB400` and emit the shared VI, task ABI/stage, SP receive, audio-join, PCM source/consumer, and drain-policy controls. On qualified arms, a tick-on-only downstream completion/PCM or a tick-off missing join selects Hdrain-required; matching qualified rows select Hdrain-redundant; missing controls select Hdrain-coverage. Report `tick_rows` separately from the positive controls.

Commands:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s2328_m5_drain_tick_ab.sh`

The recipe must launch from `build/`, use phase gates, and SIGKILL its game arms. Do not interpret pre-target nulls or change a wait/timeout based on this run.
