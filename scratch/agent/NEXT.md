# NEXT work unit (s2154) — A1 image canary span

HYPOTHESIS-ID: m5-image-canary-span

## Work unit

s2153 closed A13 busy-return polarity at the covered retail route
(`H-BusyAlwaysClear`). Do not change `osAiGetStatus_recomp` or
`osAiSetNextBuffer_recomp`.

The remaining A1 default-arm blocker is `canary_ok=0` on the already
selected legitimate `break 0`/`Broke` edge at guest PC `0x1328`. The
host plants a canary in DMEM `0xF80..0xF8F` (gap after ucode-data DMA
ending at `0xF7F`, before OSTask at `0xFC0`). Next unit is one host-only
generated census of `factor5_ucode_b` DMEM destinations in `0xF80..0xFBF`
against that reserved-gap claim. No port build, game run, canary
prefill change, task-exit mapping, default-arm, or output-route change.

## Competing hypotheses and discriminator

- `H-CanaryInWorkingSet`: the generated image has explicit DMEM
  load/store or DMA endpoints in `0xF80..0xF8F` as part of the named
  completion path (stage-3 / `break 0x1328`).
- `H-CanaryComputedOnly`: no immediate `0xF80..0xF8F` constant; the
  previously observed canary-span writes come only from computed
  pointers. Classify each such pointer's origin (task field vs overflow).
- `H-CanaryHostOnly`: the generated image never targets `0xF80..0xFBF`;
  `canary_ok=0` cannot be attributed to a named image op in this source.
- `H-CoverageFailure`: the table misses the known `0x1328` break witness
  or the stage-3 `field348+0x100` DMA (positive controls).

The discriminator is one table: every generated DMEM address or DMA
endpoint in `0xF80..0xFBF`, plus the same-file `L_1328` `break 0` and
stage-3 `lw $6, 0x348($zero)` / `addiu $6, $6, 0x100` rows as positive
controls. An explicit `0xF80..0xF8F` op selects `H-CanaryInWorkingSet`;
computed-only pointers select `H-CanaryComputedOnly`; no targets plus
live controls select `H-CanaryHostOnly`; missing controls select
`H-CoverageFailure`. Do not treat `canary_ok=0` from a prior game run as
this table.

## Exact commands

    python3 - <<'PY'
    from pathlib import Path
    p = Path('build/factor5_ucode/factor5_ucode_b_recompiled.c')
    text = p.read_text()
    print('bytes', p.stat().st_size, 'L_1328', 'L_1328:' in text)
    PY

    rg -n 'L_1328|rs64_audio_image_break|0x348|0xF80|0x0F80|RSP_MEM_.*0xF[89ABab]|dmem.*0xF[89ABab]' \
      build/factor5_ucode/factor5_ucode_b_recompiled.c

Write the classified rows to `scratch/agent/s2154_image_canary_table.txt`.
Do not edit `rsp.cpp` canary prefill, `osAiSetNextBuffer_recomp`, or the
default audio arm.
