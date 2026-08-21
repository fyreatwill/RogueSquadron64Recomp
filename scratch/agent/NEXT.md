# NEXT work unit (s2155) — A1 image DMEM write-span map

HYPOTHESIS-ID: m5-image-dmem-write-spans

## Work unit

s2154 selected `H-CanaryComputedOnly` at the host canary window: no
immediate in `0xF80..0xFBF`; computed stores from mix buffer `0xE50`
span `0x180` cover `0xE50..0xFCF` and therefore `0xF80..0xF8F`. Do not
change canary prefill, `osAiGetStatus_recomp`, `osAiSetNextBuffer_recomp`,
task-exit mapping, the default audio arm, or output routing.

The remaining A1 question is whether any unused DMEM span still exists
for a relocated host canary, or whether the image has no reserved gap
between ucode-data end (`0xF7F`) and OSTask (`0xFC0`). Next unit is one
host-only table of every generated DMEM *write* span in
`factor5_ucode_b_recompiled.c`. No port build, game run, canary prefill
change, task-exit mapping, default-arm, or output-route change.

Reuse s2154's positive controls (`L_1328` `break 0` and stage-3
`field348+0x100` DMA) and the already-classified `0xE50..0xFCF` mix
writes as same-table controls.

## Competing hypotheses and discriminator

- `H-UnusedGapExists`: at least one DMEM span in `0x000..0xFBF` is never
  written by `RSP_MEM` store, SQV/SDV/SSV, or DMA-read dest+len, and is
  large enough (>= `0x10`) to hold a canary.
- `H-NoReservedGap`: the union of write spans occupies `0xE50..0xFCF`
  continuously and leaves no unused `>=0x10` hole between ucode-data
  `0xF7F` and OSTask `0xFC0` (s2154 already shows that window is used;
  this table must show it is not an isolated overlap).
- `H-CanaryOnlyInUcodeData`: the only unused `>=0x10` spans sit inside
  `0x000..0xF7F`, which the host ucode-data DMA overwrites at task start,
  so they cannot witness the runner.
- `H-CoverageFailure`: the table misses the s2154 mix writes at
  `0xE50..0xFCF` or the `L_1328` / stage-3 controls.

The discriminator is one table: every write span (start, end, writer
label, origin: immediate / mix-buffer induction / task-field / DMA dest),
the union coverage of `0x000..0xFFF`, and the two s2154 controls. A
named unused `>=0x10` hole in `0x000..0xFBF` outside ucode-data selects
`H-UnusedGapExists`; no such hole between `0xF7F` and `0xFC0` plus the
continuous `0xE50..0xFCF` cover selects `H-NoReservedGap`; unused holes
only inside `0x000..0xF7F` select `H-CanaryOnlyInUcodeData`; missing
controls select `H-CoverageFailure`. Do not treat prior `canary_ok=0`
rows as this table.

## Exact commands

    python3 - <<'PY'
    from pathlib import Path
    p = Path('build/factor5_ucode/factor5_ucode_b_recompiled.c')
    text = p.read_text()
    print('bytes', p.stat().st_size, 'L_1328', 'L_1328:' in text)
    PY

Parse every `RSP_MEM_*STORE` / `RSP_MEM_B(...) =`, `rsp.S[QDS]V`,
`SET_DMA_MEM` used by `DO_DMA_READ`, and classify dest+len. Include
`L_1CDC`/`L_15F8`/`L_1EF0` `0xE50` spans as controls.

Write the classified rows to `scratch/agent/s2155_image_dmem_write_spans.txt`.
Do not edit `rsp.cpp` canary prefill, `osAiSetNextBuffer_recomp`, or the
default audio arm.
