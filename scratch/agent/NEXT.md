# NEXT work unit (s2199) — test VI field alternation

HYPOTHESIS-ID: m5-a1-vi-field-alternation

## Work unit

Add one runtime-gated branch to `ViState::update_vi` that toggles its
`field` selector after each VI update when
`ROGUESQ_VI_ALTERNATE_FIELDS=1`; leave the existing behavior unchanged for
`=0`. Do not add another diagnostic field: reuse the s2198 boundary table and
the existing caller, writer, and phase controls. Because `lib/N64ModernRuntime`
is edited, run `./submodule-patches/export.sh` before the single build.

## Competing hypotheses and discriminator

- H-ViFieldNotToggled: the missing `field` writer is the boundary; only the
  `=1` arm reaches repeated 640 origins `0x00696100` and `0x00696600`, with
  matching commit and screen rows.
- H-SecondOriginElsewhere: both arms pass controls but neither reaches
  `0x00696600`; field selection is not the route boundary.
- H-FieldCalculationMismatch: `=1` changes VI origins but commits neither
  expected target (or changes the requested framebuffer unexpectedly).
- H-CoverageFailure: either arm lacks the caller/writer/first-origin control;
  reject that arm rather than interpreting its null as evidence.

The single comparison is the phase-gated boundary table in both arms. A
positive arm must show `[vi-callers-control]`, writer rows, and repeated 640
rows at both target origins. `=1` producing both target origins while `=0`
remains first-origin-only selects H-ViFieldNotToggled; positive controls in
both arms with no second origin selects H-SecondOriginElsewhere; unexpected
origins or framebuffer values selects H-FieldCalculationMismatch.

## Build and run

```sh
./submodule-patches/export.sh
cmake --build build --config Debug --target RogueSquadron64Recomp

env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_M5_WRITER_PARITY=1 ROGUESQ_LOG_VI_COMMIT=1 ROGUESQ_VI_ALTERNATE_FIELDS=0" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s2199_vi_field_off 30 12 > scratch/agent/s2199_vi_field_off_driver.log 2>&1 &
off=$!
env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_M5_WRITER_PARITY=1 ROGUESQ_LOG_VI_COMMIT=1 ROGUESQ_VI_ALTERNATE_FIELDS=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s2199_vi_field_on 30 12 > scratch/agent/s2199_vi_field_on_driver.log 2>&1 &
on=$!
wait "$off"; off_rc=$?
wait "$on"; on_rc=$?
printf 'off_rc=%s on_rc=%s\n' "$off_rc" "$on_rc"
```

Accept only arms with positive controls and phase-gated boundary rows; do
not add a guard, mitigation, task rewrite, or audio-default change.
