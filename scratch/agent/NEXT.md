# NEXT work unit — retail: viewer frame-loop exit vs anyAudioSlotActive tail

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

Session 3284 selected `H-RetailViewerThenReturn`: first
`menuOverlayInit` (`$a1=9`) jal's `runMenuModelViewerScreen`
(`0x800C28F0`) at 2.5 s (`prev_pc=0x800C5C98`) and returns at 6.7 s.
The generated body has two sequential waits: a frame loop that exits
when `$s5=1` (`0x800C2B88`, `$f24` fade to 0), then
`anyAudioSlotActive` until `$v0 != 0` (`L_800C2DB0`). s3278's port
log entered the screen and never reached
`[slot-ret-caller] site=runMenuModelViewerScreen`, so the port is
still in the frame loop. Ask retail which gate actually occupies
2.5–6.7 s.

Do not use `--pc-phase-log-width` unless 320 origins are listed.

If the no-engineering pivot preamble is present (streak hits 6 after
s3284), also land matching regeneration-preserved port counters at
`0x800C2B88` / `0x800C2DB0` / `0x800C2E00` in `tools/fixup_*.py` in
this same iteration. Do not add a skip, allow, restore, or wait
bypass. No M5 Step 3. No local `PatchesLib` build.

## Competing hypotheses

- `H-RetailFrameTimerThenBriefSlot`: `0x800C2B88` then `0x800C2DB0`
  then `0x800C2E00` clustered near the 6.7 s `0x8003E094`. Retail
  spends 2.5–6.7 s in the frame loop; the slot wait is one or a few
  hits. The port is stuck on the fade/timer, not A11.
- `H-RetailLongSlotWait`: `0x800C2DB0` fires near 2.5 s and
  `0x800C2E00` at 6.7 s. Retail spends most of the interval on
  `anyAudioSlotActive`. Does not explain the s3278 port (it never
  reached that tail) unless the port never leaves the frame loop
  for a different reason.
- `H-RetailNoFadeStore`: `0x800C2E00` fires without `0x800C2B88`.
  Another `$s5=1` path, or `bc1tl` nullified the watched delay slot.
- `H-ExitCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing, or the 6.7 s `0x8003E094` watch silent (failed
  instrument).

## Discriminator

One retail Rice run. Exec-watch `0x800C2B88`, `0x800C2DB0`,
`0x800C2E00`, `0x8003E094` in the same run, armed at first VI.
Printed times vs 2.5 s viewer entry (s3284) vs 6.7 s return select
frame-timer / long-slot / no-fade. `0x800C2B88` is the `bc1tl`
delay slot that stores `$s5=1` only when `$f24==0`; overlay-alias
hits need `prev_pc` inside `0x800C28F0..0x800C2E08`.

Positive control: `--watch-write 0x0:0x800000` must hit (cap 10000)
AND `--vi-trace` must show title `1024 @ 0x00790400` AND `[gpr-ctl]`
/ an exec hit at `0x8003E094` must fire. A silent `0x8003E094` watch
is a failed instrument. Lifetime `exec-prev` still counts past
EXEC_LOG_CAP 64.

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
  --watch-pc 0x800C2B88,0x800C2DB0,0x800C2E00,0x8003E094 \
  --vi-trace --vi-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s3285_viewer_frame_exit.log 2>&1
```

No `--pc-phase-log-width`. Join printed `0x800C2B88` / `0x800C2DB0`
times to `0x800C2E00` and the 6.7 s `0x8003E094`. Do not change
audio behavior.
