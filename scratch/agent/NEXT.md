# NEXT work unit (s2161) — retail wait-slot count-byte ground truth

HYPOTHESIS-ID: m5-image-wait-slot-sigsegv

## Work unit

s2160 selected `H-RouteRegress` and reverted A1 default-on. Unset and
`ROGUESQ_AUDIO_UCODE=1` both SIGSEGV in `waitForAnyAudioSlot+1060` from
`menuOverlayInit` at 640 `0x0066A500` (`si_addr=0x400141ad3`, host XOR-3
of guest `D_80141AD0`). Stub `=0` returns from that wait and reaches
title/hangar. Do not add a wait/slot guard, retry default-on, move the
canary, or change `osAiGetStatus_recomp` / `osAiSetNextBuffer_recomp`.

Ask retail before another port instrument. Guest `func_800668B0`
(`waitForAnyAudioSlot`) is 0x68 bytes; the jal site is `0x800C5CF4`.

## Competing hypotheses and discriminator

- `H-RetailLoadsCount`: retail executes `0x800668B0` during boot and
  reads physical `0x141AD0` from that PC (or a jal it makes). The count
  byte is legitimate; the port crash is translation or walk bounds.
- `H-RetailNeverLoads`: whole-RDRAM control fires and `0x800668B0`
  executes, but the `0x141AD0` read watch is zero. The port image path
  is extra/wrong at this site.
- `H-RetailWritesThenReads`: retail writes `0x141AD0` from a named PC,
  then `0x800668B0` reads it. That writer is the ORIGIN candidate.
- `H-CoverageFailure`: `0x800668B0` never executes (oracle stays short
  of menuOverlayInit). Nulls are uninterpretable.

Positive control: `--watch-write 0x0:0x800000` must fire (whole-RDRAM
~1.6M hits in 8 emulated seconds). `--watch-pc 0x800668B0` must print
at least one exec hit before a `0x141AD0` null is treated as evidence.

## Exact commands

From the repo root, after confirming `tools/oracle/build/rs64_oracle`
and the README core/ROM paths exist:

    tools/oracle/build/rs64_oracle \
      --core ~/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom  ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --secs 45 --vi-trace \
      --watch-write 0x0:0x800000 \
      --watch-read  0x141AD0:0x141AD4 \
      --watch-write 0x141AD0:0x141AD4 \
      --watch-pc    0x800668B0,0x800C5CF4 \
      --first-watch 0 --pc-hist-watch 1 --pc-hist-watch 2

Arm the whole-RDRAM write first. Physical addresses only. If the
positive control does not fire, stop; do not interpret the count-byte
nulls.

Do not change `get_rsp_microcode`, canary prefill, wait pumps, or
guest gates in this unit.
