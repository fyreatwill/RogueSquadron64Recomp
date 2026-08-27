# NEXT work unit (s2836) — invert audio-arm launch order

HYPOTHESIS-ID: m5-audio-route-launch-order

## Work unit

Run one same-build image/silent pair with the launch order inverted: launch
the image arm first, then the silent arm. Keep the same 16-event schedule and
all existing phase/audio markers, plus the whole-RDRAM retail positive control.
Do not change audio behavior or add a guard. This tests whether the s2835
image-at-320 versus silent-at-640 divergence is scheduling-sensitive.

## Competing hypotheses and discriminator

- H-launch-order: image reaches VI 640 or later when given the first-process
  slot, and the prior divergence was scheduling-sensitive.
- H-intrinsic-image-stall: image remains at VI 320 while silent reaches VI 640
  despite the inverted launch order.
- H-nondeterministic-route: the terminal phase changes without a stable
  image-first advantage, so launch order alone does not explain the split.

The discriminator is one run containing both arms and the retail control.
Image reaching VI 640/title/hangar with silent still reaching VI 640 selects
H-launch-order; image remaining at VI 320 while silent reaches VI 640 selects
H-intrinsic-image-stall; a different unstable split selects
H-nondeterministic-route. Only after a target phase is reached may M5 contract
rows be interpreted.

## Exact commands

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2836_m5_launch_order.sh
grep -a -E 'oracle_gate|title=|hangar=|\[phase\] vi_width=|\[autopilot\]|\[audtask-dispatch\]|\[CRASH\]|\[ABORT\]' scratch/agent/s2836_m5_launch_order/driver.log
```

The new recipe must SIGKILL its process group and must treat pre-target audio
nulls as unevaluable.
