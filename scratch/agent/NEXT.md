# NEXT work unit (s2022)

HYPOTHESIS-ID: m5-service-body-store-boundary

## RESUME: s2021 direct-entry result

s2021 clean-regenerated the external tree, built the port, and ran the
phase-valid mission-key recipe. The target `serviceVoicePoolFrame` emitted
2,096 `[s2020-svc]` phase-valid entries and 2,096 exits. The bounded
pre-phase entry control emitted zero rows. Every sampled entry had
`thr=0 status=0x00 ra=0`, so the derived call site was `0xFFFFFFF8`, not the
retail `0x80019B74`. The independent s2006 entry/exit control fired, but no
`[s2006-store]` row for `0x8009B7EC` fired. VI 1024 and VI 512 both arrived;
the run later hit the known arm64 SIGBUS boundary at guest PC `0x80054780`.

This selects D4 from the s2020 table: the service target is reached and
returns, but the worker-side clear edge is not. Do not repeat the direct-entry
or `get_function` witness alone, and do not proceed to the seven-site writer
join until the body reaches or explains the missing store.

## Work unit

Add one phase-gated `[s2022-svc]` body census to `serviceVoicePoolFrame` in
`../N64Recomp/fixup_game_funcs.py`. Keep the s2020 entry/exit rows, the s2006
entry/exit/store control, and all behavior unchanged. Add bounded pre-phase
body controls and phase-valid rows at all three edges in one build:

- At the `0x8009B5D8` branch, record `rs64_phase_ord()`, guest thread,
  `0x800A5121` gate byte, slot-0 status, and `path=skip` versus `path=body`.
- At the `0x8009B624` slot-loop head, record the loop slot index, status byte,
  phase, thread, and whether the `0x8009B630` zero-status skip was taken.
- At the actual `0x8009B7EC` store, record the effective slot, old/new byte,
  phase, thread, and shutdown call. This edge must be independently bounded,
  not hidden behind the s2006 `status==3 || first-24` condition.

Use a first-10 pre-phase control at the branch and loop, plus phase-gated
rows reset per phase. The same-run positive controls are the existing s2020
entry/exit rows and the s2006 entry rows; interpret body nulls only if those
controls fire.

## Competing hypotheses and discriminator

- H1: `0x800A5121` is zero when the target runs, so every call takes the
  `0x8009B5D8` skip path and never reaches the voice loop/store.
- H2: the gate is nonzero and the body reaches `0x8009B624`, but all observed
  slot statuses take the `0x8009B630` zero-status skip or another body branch.
- H3: the actual store fires but the old s2006 condition/logging arm missed it.

The discriminating measurement is the same-run table of gate path, loop-head
rows, zero-status skip rows, and independent actual-store rows. H1 is selected
by gate=0 plus skip-only; H2 by gate nonzero plus loop activity and no store;
H3 by an actual `[s2022-svc] edge=store` row. If none of the body edges fire
while s2020 entry/exit controls are live, the fixup anchor or generated branch
crosswalk is wrong and the work unit is not evaluable.

## Regeneration, build, and run

```sh
set -e
backup_dir=$(mktemp -d /tmp/rs64-s2022-recompiled.XXXXXX)
cp -a /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/. "$backup_dir/"
find /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs -mindepth 1 -maxdepth 1 -type f -delete
cd /Users/williambuckley/Documents/Tools/rogue_squadron64
python3 tools/make_elf.py
cd /Users/williambuckley/Documents/Tools/N64Recomp
build/N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py
env RS64_S2006_STATUS3=1 python3 fixup_game_funcs.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2022-service-body 30 12
```

Extract with:

```sh
RUN=scratch/s73_post_a_scene/s2022-service-body/run.log
rg -n -e '\[s2022-svc\]' -e '\[s2020-svc\]' -e '\[s2006-svc\]' -e '\[service-voice-pool-frame\]' -e 'audio-gate-raw|audio-drain|\[phase\]' "$RUN" | tail -260
```
