# NEXT work unit (s2100)

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Add one regeneration-stable diagnostic to the Factor 5 image arm and run the
qualified same-build control/treatment pair. The diagnostic must emit one
phase-keyed row per reachable image-task stage, joined by the existing audio
route ordinal:

- before `L_19A4`: FNV/nonzero summary of DMEM `0xCC0..0xE3F`, the loaded
  `0x348` pointer, and the active `r2` descriptor block;
- at `L_12D0`, immediately before `L_1830`: FNV/nonzero summaries of
  `0x3F0..0x56F` and `0x570..0x6EF`;
- at `L_12E0`, immediately before its `DO_DMA_WRITE`: FNV/nonzero summary
  of `0x6F0..0x9EF`, `[r2+0x44]`, and the 0x300-byte destination;
- at `L_1314`, immediately before its `DO_DMA_WRITE`: FNV/nonzero summary
  of `0xCB0..0xE47`, `[0x348]+0x100`, and the 0x198-byte destination.

Implement the generated-file changes in `tools/fixup_factor5_ucode.py`,
keyed specifically to `factor5_ucode_b_recompiled.c`; do not hand-edit the
generated C. Add only the host logging stub needed in `src/main/main.cpp`.
Keep the ucode behavior unchanged. Build once after fixup and run both arms
from the same eleven-Start driver with `ROGUESQ_SPIN_YIELD=1` in both arms.

## Competing hypotheses and discriminator

- **H-InputZero** — the pre-`L_19A4` `0xCC0..0xE3F` source is zero or
  legitimately silent, and the transform/output spans are correspondingly
  zero.
- **H-TransformAnnihilation** — the source is nonzero but the generated
  transform produces a zero `0x3F0/0x570` result under the observed task
  coefficients.
- **H-RSPWriteLoss** — nonzero source survives into both the transform and
  pre-DMA `0x6F0` span, while the independent DMA-range rows still report a
  zero copied payload.
- **H-ABI-Destination** — the source/output table is live, but either
  destination field is zero, unstable, or points to a control structure whose
  meaning is not host PCM output.

The discriminator is one complete table joined on arm, phase, route ordinal,
and task ordinal: source FNV/nonzero, transform FNV/nonzero, pre-DMA output
FNV/nonzero, both destination values, matching `audtask-dma-range` counts and
payload flags, and the existing ABI/route rows. Source zero plus transform
zero selects `H-InputZero`; nonzero source plus zero transform selects
`H-TransformAnnihilation`; nonzero source/transform/output plus zero copied
payload selects `H-RSPWriteLoss`; unresolved or control-like destination
values retain `H-ABI-Destination` at field-contract scope. Do not infer from
DMEM changed counts or a branch-entry counter alone.

The positive controls are required in the same run: both arms must show the
existing complete return -> SP completion -> external delivery -> guest
receive route; the control must reach title and hangar; the treatment must
emit all four stage markers and have each pre-DMA row cross-check against an
existing DMA-range row. A stage marker by itself is not a data-validity
control.

## Exact commands

```sh
rg -n 'L_1104:|L_12D0:|L_12E0:|L_1314:|factor5_ucode_b\(' build/factor5_ucode/factor5_ucode_b_recompiled.c tools/fixup_factor5_ucode.py
rg -n 'audio.*dma|audtask-dma-range|rs64_audio_route_snapshot' src/main/main.cpp lib/N64ModernRuntime/librecomp/src/rsp.cpp
python3 tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_b_recompiled.c
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step7-treatment 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step7-treatment-driver.log 2>&1 &
pid_t=$!
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step7-control 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step7-control-driver.log 2>&1 &
pid_c=$!
wait $pid_t; rc_t=$?
wait $pid_c; rc_c=$?
printf 'treatment_rc=%s control_rc=%s\n' "$rc_t" "$rc_c"
```

Do not change output routing, task fields, canary, gate, wait, guard, queue
policy, or default dispatch. If the static fixup anchors cannot be made
regeneration-stable, stop before building and record the exact anchor failure
as the result rather than hand-editing the generated file.
