# NEXT work unit — RESUME: retail delay-slot vs beq-path discriminator

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3285 selects `H-RetailNoFadeStore`: retail first `menuOverlayInit`
returns from `runMenuModelViewerScreen` at 6.8 s through the slot jal
(`0x800C2DB0` → `0x800C2E00`) without executing `0x800C2B88` (`$s5=1` delay
slot). Session 3286 was a checkpoint close-out; the oracle below did NOT run.

Run the oracle now exactly as written — do not modify it.

## Competing hypotheses

- `H-DelaySlotWatchMiss`: `0x800C2B84` (`bc1tl`) fires near 6.8 s and
  `0x800C2D50` then `0x800C2DA0` follow. Mupen does not report the
  nullifiable delay-slot PC `0x800C2B88` even when the branch is taken.
  The fade store ran.
- `H-BeqTakenWithoutFadeStore`: `0x800C2D50` fires and `0x800C2DA0`
  follows, but `0x800C2B84` is silent. `$s5` matches `$v0` without the
  fade store (another writer, or `$v0` is 0).
- `H-Da0WithoutBeq`: `0x800C2DA0` / `0x800C2DB0` fire without
  `0x800C2D50`. Another path into the slot tail.
- `H-ExitCoverageInvalid`: whole-RDRAM control or title 1024 missing,
  or the 6.8 s `0x800C2E00` watch silent (failed instrument).

## Discriminator

One retail Rice run. Exec-watch `0x800C2B84`, `0x800C2D50`,
`0x800C2DA0`, `0x800C2E00` in the same run, armed at first VI.
Printed times vs the known 6.8 s return. Overlay-alias hits need
`prev_pc` inside `0x800C28F0..0x800C2E08`.

Positive control: `--watch-write 0x0:0x800000` must hit (cap 10000)
AND `--vi-trace` must show title `1024 @ 0x00790400` AND an exec hit
at `0x800C2E00` must fire at ~6.8 s. A silent `0x800C2E00` watch is a
failed instrument.

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
  --watch-pc 0x800C2B84,0x800C2D50,0x800C2DA0,0x800C2E00 \
  --vi-trace --vi-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s3287_viewer_s5_exit.log 2>&1
```

No `--pc-phase-log-width`. Join printed `0x800C2B84` / `0x800C2D50`
times to `0x800C2DA0` and the 6.8 s `0x800C2E00`. Do not change audio
behavior. Log file is `s3287_viewer_s5_exit.log` (next session number).
