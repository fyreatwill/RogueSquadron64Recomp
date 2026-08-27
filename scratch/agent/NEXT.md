# NEXT work unit (s2837) — barrier image initialization before silent launch

HYPOTHESIS-ID: m5-audio-route-init-barrier

## Work unit

Run one same-build image/silent pair with an initialization barrier: launch
the image arm first, wait until its log has at least four positive
`[audtask-dispatch]` rows, then launch the silent arm. Keep the same 16-event
schedule and all existing phase/audio markers, plus the whole-RDRAM retail
positive control. Do not change audio behavior or add a guard. This tests
whether the split depends on whether the second process starts during image
initialization.

## Competing hypotheses and discriminator

- H-init-race: delaying silent until image initialization has progressed
  changes the pair outcome, selecting an initialization race.
- H-image-route-defect: image remains at VI 320 while silent reaches VI 640
  with the barrier, selecting an image-route defect.
- H-schedule-noise: the result is another 640/640 or an unstable split without
  a repeatable barrier effect, rejecting this scheduling explanation.

The discriminator is one run containing both arms and the retail control.
Image reaching VI 640/title/hangar after the barrier while the unbarriered
s2835 image was at VI 320 selects H-init-race; image remaining at VI 320 while
silent reaches VI 640 selects H-image-route-defect; another 640/640 or an
unstable split selects H-schedule-noise. Only after a target phase is reached
may M5 contract rows be interpreted.

## Exact commands

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2837_m5_init_barrier.sh
grep -a -E 'oracle_gate|title=|hangar=|\[phase\] vi_width=|\[autopilot\]|\[audtask-dispatch\]|\[CRASH\]|\[ABORT\]' scratch/agent/s2837_m5_init_barrier/driver.log
```

The new recipe must SIGKILL its process group and must treat pre-target audio
nulls as unevaluable.
