# NEXT work unit (s2065)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Perform one bounded static ABI audit of the image task's final DMA/writeback
path. Starting from every `DO_DMA_READ` and `DO_DMA_WRITE` in
`factor5_ucode_b_recompiled.c`, compute the effective DMEM span and RDRAM
source/destination, then compare those spans with the staged OSTask fields
(`output_buff`, `data_ptr`, `yield_data_ptr`) and the s2063 zero-payload joins.
Classify the `0xE50..0xFCF` generated work stream as scratch, output staging,
or an ABI mismatch. Do not change runtime code, task fields, canary framing,
dispatch, or guest behavior; do not build or run a soak.

## Competing hypotheses and discriminator

- **H-ImageWorkScratch** — `0xE50..0xFCF` is intentional image-local DMEM
  scratch, while the final task output is the `L_1314` DMA from a distinct
  source range; the canary overwrite is unrelated to the zero PCM join.
- **H-ImageOutputStaging** — the `0xE50..0xFCF` stream is the image's output
  staging buffer, but the final DMA selects only a subrange or a zero-filled
  source, so the task contract is incomplete rather than host-mutated.
- **H-ImageTaskAbiMismatch** — an effective DMEM/RDRAM offset or length is
  inconsistent with the OSTask fields or image layout, explaining the canary
  overwrite and zero DMA payload as an ABI mismatch.
- **H-OutputRouteUnevaluable** — an effective address/length or its relation to
  the task fields cannot be proven from the generated source and host macros;
  do not add a mitigation or select a theory.

The discriminator is one complete table with one row per generated DMA site:
site/label, direction, effective DMEM span, effective RDRAM span, controlling
register formula, and matching OSTask field (or `none`). A complete match to
an intentional scratch/output layout selects H-ImageWorkScratch or
H-ImageOutputStaging; an offset/length mismatch selects H-ImageTaskAbiMismatch;
any unproved row selects H-OutputRouteUnevaluable.

## Exact commands

Use bounded source windows and preserve the resulting table in the session
entry; no regeneration, build, game run, or soak is authorized for this unit:

```sh
rg -n 'DO_DMA_(READ|WRITE)|SET_DMA_(MEM|DRAM)|L_13E8|L_1418|L_1314|L_1924|L_1D68|L_1E00|L_1E04|L_1E48' \
  build/factor5_ucode/factor5_ucode_b_recompiled.c
sed -n '630,770p' build/factor5_ucode/factor5_ucode_b_recompiled.c
sed -n '500,550p' build/factor5_ucode/factor5_ucode_b_recompiled.c
sed -n '88,100p' lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp
sed -n '300,335p' lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp
sed -n '350,365p' lib/N64ModernRuntime/librecomp/src/rsp.cpp
sed -n '1200,1240p' src/main/main.cpp
rg -n 'output_buff|data_ptr|yield_data_ptr|audtask-dma-range|H-ImageDmaStagingOnly' \
  docs/CURRENT-TRUTH.md docs/M5-AUDIO-PLAN.md PORTING-STATE.md | tail -80
git diff --check
```

ORIGIN: s2064 attributed the canary and `Broke` result to generated guest
stores and the natural `L_1328` break; this unit maps the final task ABI before
any output, skip, or guard interpretation is considered.
