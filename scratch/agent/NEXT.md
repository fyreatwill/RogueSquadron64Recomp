# Next work unit: repair the M5 drain-tick gate predicate and rerun the A/B

HYPOTHESIS-ID: m5-drain-tick-gate-contract-repair

Repair the stale qualification predicate in `scratch/agent/run_s2328_m5_drain_tick_ab.sh`: the current binary has no `[drain-inloop-gate]` string, while its live `[drain-tick]` rows carry `gate=0x00`. Use the live drain-tick row count and parsed gate field as the policy control, retain the oracle and all existing phase/task/SP/slot/PCM controls, and run the image arms with `DRAIN_TICK_ORDER=image-off-first`. Do not change the runtime policy.

Competing hypotheses:

- Hdrain-required: after predicate repair, tick-off loses a downstream or drain-tick control that tick-on retains.
- Hdrain-redundant: both image arms qualify with matching downstream joins and only the explicit tick-row policy field differs.
- Hdrain-coverage: the live `[drain-tick]` rows or another shared positive control remain absent, so the comparison is unevaluable.

Discriminating measurement: the oracle must pass its whole-RDRAM and retail title/hangar controls. Both image arms must reach port hangar `512 @ 0x006AB400`, emit the shared VI/task ABI/stage/SP/audio-join/PCM controls, and produce parsed `[drain-tick]` rows. A tick-on-only downstream completion/PCM or tick-off missing join selects Hdrain-required; matching qualified rows select Hdrain-redundant; missing live rows select Hdrain-coverage. Report tick row counts and gate field values separately.

Commands:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env DRAIN_TICK_ORDER=image-off-first zsh scratch/agent/run_s2328_m5_drain_tick_ab.sh s4103_m5_drain_tick_gate_repaired`
