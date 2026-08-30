# NEXT work unit — retail: does first menuOverlayInit run runMenuModelViewerScreen?

HYPOTHESIS-ID: m5-osvimode-first-menu-model-viewer

Session 3283 selected `H-FirstReturnsThenCinematic`: first
`menuOverlayInit` (`$a1=9` at 2.0 s) returns at 6.9 s
(`0x8003E094`, `prev_pc=0x800C5D94`); `cinematicLoopBody` jal
`0x8003E10C` / entry `0x800A5D80` occupies 6.9–17.0 s; second
menu jal `0x8003E13C` at 17.0 s then title 1024. Iron rule 12:
the port's s3278 census entered `runMenuModelViewerScreen`
(`0x800C28F0`) at `640 @ 0x66A500` during that first activation
and never logged a return. Ask retail whether that screen is on
the first-menu path.

Do not use `--pc-phase-log-width` unless 320 origins are listed:
that flag defers `--watch-pc` until the first matching bucket.

## Competing hypotheses

- `H-RetailViewerThenReturn`: `0x800C28F0` fires during 2.0–6.9 s
  (first `$a1=9` activation); `0x8003E094` still at 6.9 s. Retail
  enters and leaves the model viewer; the port is stuck inside a
  screen retail also uses.
- `H-RetailNoViewer`: `0x800C28F0` silent before `0x8003E094`.
  The port's model-viewer entry is a mis-dispatch, not retail's
  first-menu path.
- `H-RetailViewerAfterCine`: `0x800C28F0` fires only after the
  17 s `0x8003E13C` (second menu). The port entered it too early.
- `H-ViewerCoverageInvalid`: whole-RDRAM control or title 1024
  gate missing, or the 6.9 s `0x8003E094` watch silent (failed
  instrument).

## Discriminator

One retail Rice run. Exec-watch `0x800C28F0`, `0x8003E094`,
`0x800A5D80`, `0x8003E13C` in the same run, armed at first VI.
Printed `0x800C28F0` time vs 6.9 s return vs cinematic vs 17 s
jal selects during-first / never-in-first / only-after-cinematic.
Classify overlay-alias hits at `0x800C28F0` by `prev_pc` (must be
inside `menuOverlayInit` `0x800C58A0..0x800C5D9C` to count as
first-menu). Boot/320 `0x800C28F0` is still a first-activation
hit.

Positive control: `--watch-write 0x0:0x800000` must hit (cap 10000)
AND `--vi-trace` must show title `1024 @ 0x00790400` AND `[gpr-ctl]`
/ an exec hit at `0x8003E094` must fire (the 6.9 s first return is
enough to prove the watch). A silent `0x8003E094` watch is a failed
instrument. The 17 s `0x8003E13C` hit is a second timeline anchor,
not required to classify the viewer.

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
  --watch-pc 0x800C28F0,0x8003E094,0x800A5D80,0x8003E13C \
  --vi-trace --vi-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s3284_first_menu_model_viewer.log 2>&1
```

No `--pc-phase-log-width`: exec watches arm on first VI (covers 320).
Join printed `0x800C28F0` times to `0x8003E094` / `0x800A5D80` and
the 17 s `0x8003E13C`. Lifetime `exec-prev` still counts past
EXEC_LOG_CAP 64. Do not change audio behavior. Do not run M5 Step 3.
Do not repeat the local missing-target `PatchesLib` build.
