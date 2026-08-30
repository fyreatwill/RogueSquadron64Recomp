# NEXT work unit — retail: first menuOverlayInit return vs cinematic vs 17 s jal

HYPOTHESIS-ID: m5-osvimode-menu-return-vs-cinematic

Session 3282 selected `H-MenuReentry`: two `menuOverlayInit` entries,
each with an immediate jal. The 17.0 s 1024-edge jal is
`mainGameLoop` `0x8003E13C` (`$a1=2`), not a wait inside the 2.0 s
`0x8003E08C` (`$a1=9`) activation. Because `0x8003E13C` ran, the
first call returned before 17 s. Iron rule 12: ask retail what
occupies the 15 s gap.

Do not use `--pc-phase-log-width` unless 320 origins are listed:
that flag defers `--watch-pc` until the first matching bucket.

## Competing hypotheses

- `H-FirstReturnsThenCinematic`: continuation `0x8003E094` fires at
  ~2 s; `cinematicLoopBody` jal `0x8003E10C` / entry `0x800A5D80`
  occupies the gap; `0x8003E13C` at ~17 s.
- `H-FirstStaysResident`: `0x8003E094` fires only at ~17 s, immediately
  before `0x8003E13C`. First `menuOverlayInit` is the long inner loop.
- `H-GapIsOtherMainWork`: `0x8003E094` at ~2 s, zero classifiable
  cinematic exec, `0x8003E13C` still at ~17 s.
- `H-ReturnCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing, or the 17 s `0x8003E13C` watch silent (failed instrument).

## Discriminator

One retail Rice run. Exec-watch `0x8003E094`, `0x8003E10C`,
`0x800A5D80`, `0x8003E13C` in the same run, armed at first VI.
Printed `0x8003E094` time vs cinematic time vs 17 s `0x8003E13C`
selects short-then-cinematic / long-first / other-work.
Classify overlay-alias hits at `0x800A5D80` by `prev_pc`
(`mainGameLoop` `0x8003E10C` vs cinematic-resident). Boot/320
`0x8003E094` is coverage for the first return, not the 17 s
discriminator.

Positive control: `--watch-write 0x0:0x800000` must hit (cap 10000)
AND `--vi-trace` must show title `1024 @ 0x00790400` AND `[gpr-ctl]`
/ an exec hit at `0x8003E13C` must fire (the 17 s second jal is
enough to prove the watch). A silent `0x8003E13C` watch is a failed
instrument.

Require Rice. Dummy video stays at 320 / `0x006dd280` forever.

## Exact command

From the repository root:

```sh
tools/oracle/build/rs64_oracle \
  --core ~/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom  ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 25 --hit-cap 10000 \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x8003E094,0x8003E10C,0x800A5D80,0x8003E13C \
  --vi-trace --vi-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s3283_menu_return_vs_cinematic.log 2>&1
```

No `--pc-phase-log-width`: exec watches arm on first VI (covers 320).
Join printed `0x8003E094` times to `0x800A5D80` / `0x8003E10C` and
the 17 s `0x8003E13C`. Lifetime `exec-prev` still counts past
EXEC_LOG_CAP 64. Do not change audio behavior. Do not run M5 Step 3.
Do not repeat the local missing-target `PatchesLib` build.
