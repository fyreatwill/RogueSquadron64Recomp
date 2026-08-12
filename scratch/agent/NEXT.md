# NEXT work unit (after s691 recovery-negative command capture)

HYPOTHESIS-ID: m3-recovery-latch-readiness

Before another `L_12A0` capture, audit the recovery-latch gate that made s691
unscorable. The exact s670 recipe previously produced a qualified s689 row,
but s691 completed 9/9 hangar-selection-engaged attempts without one
`0x0076B768` event. Do not change decoding, submission, or FULL_SYNC.

## Competing hypotheses

- **H-config-drift:** the recovery-active s689 invocation differs from the
  current script or inherited environment in a force/gate setting.
- **H-wrapper-observer-loss:** recovery occurs but the watcher/log selection
  fails to observe `0x0076B768`.
- **H-stochastic-route:** invocation and observer are intact; recovery is a
  probabilistic branch that happened not to fire in s691.

## Discriminating measurement

Make one bounded, regeneration-free audit script that records complete
effective `GAME_EXTRA_ENV`, relevant inherited `ROGUESQ_FORCE_*` settings,
and two independent recovery observations from the same `run.log`: the literal
`0x0076B768` and the surrounding `[fs-slot]`/`[rdp-fullsync]` transition. Run
the s689-compatible and current-script arms concurrently, phase-gated, one
attempt each. Positive controls: a boot `[e9-prov]` chain in each new arm and
the recovered transition in the saved s689 log parsed by the same scorer.

- Different effective settings or force banners: H-config-drift supported.
- Independent transition but no literal watch hit: H-wrapper-observer-loss.
- Matching arms/configs and controls, both without transition: H-stochastic-route.
- Missing saved-log or boot controls: reject and repair the scorer first.

## Commands

    rg -n '0076B768|\[fs-slot\]|\[rdp-fullsync\]|\[e9-prov\]' scratch/s73_post_a_scene/s670_postsec2_pulse_1_20260812051415/run.log | head -200
    sed -n '1,240p' scratch/agent/s670_postsec2_pulse_freeroll.sh
    sed -n '1,240p' scratch/agent/s670_run_mission_keys_postsec2.sh
