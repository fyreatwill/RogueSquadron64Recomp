# NEXT work unit — retail: who calls initVideoSubsystem at the 1024 rewrite?

HYPOTHESIS-ID: m5-osvimode-1024-rewrite-caller

Session 3279 selected `H-RetailTableHas1024`: while title 1024 is live, all
four OSViMode slot +8 words are 1024. The only writer is `0x8001B6B0`
inside `initVideoSubsystem` (`0x8001A098`, size `0x1720`), at the 640→1024
edge. Session 3278's port census never saw that 1024 copy. Iron rule 12:
ask retail which caller performs the title-edge invocation before assuming
the port should already have run it during VI 640.

## Competing hypotheses

- `H-RewriteCallerPreTitle`: the 1024-edge `initVideoSubsystem` entry's
  `prev_pc` is a caller the port already reaches during VI 640. The port
  is missing that call (cause of `H-MissingTableRewrite`).
- `H-RewriteCallerTitleEntry`: that entry's `prev_pc` is a title-entry /
  post-640-only caller. The missing 1024 copy is a symptom of never
  leaving VI 640, not the publisher that would leave it.
- `H-RewriteNotANewEntry`: `0x8001A098` does not execute at the 17.3 s
  copy; `0x8001B6B0` runs inside a long-lived activation. Attribute via
  the live `$ra` / surrounding PC, not a fresh jal.
- `H-CallerCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing, or the entry watch never fires (failed instrument).

## Discriminator

One retail Rice run. Exec-watch `initVideoSubsystem` entry `0x8001A098`.
A printed exec at ~the 640→1024 edge with `prev_pc` selects
`H-RewriteCallerPreTitle` or `H-RewriteCallerTitleEntry` by whether that
caller is on the port's already-reached VI-640 path. Title-edge copy with
no new entry selects `H-RewriteNotANewEntry`.

Positive control: `--watch-write 0x0:0x800000` must hit (cap 10000) AND
`--vi-trace` must show title `1024 @ 0x00790400` AND `[gpr-ctl]` / an
exec hit at `0x8001A098` must fire (boot entry is enough to prove the
watch). A silent entry watch is a failed instrument.

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
  --watch-pc 0x8001A098 \
  --watch-write 0x128D58:0x128D5C \
  --detail-watch 1 \
  --pc-hist-watch 1 \
  --pc-hist-phase 0x0066A500:640 \
  --pc-hist-phase 0x00790400:1024 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace --vi-poll \
  > scratch/agent/s3280_initvideo_caller.log 2>&1
```

`--secs 25` stops in the title window (1024 live, hangar not yet). Slot
watch 1 is the same-run join: a `0x8001B6B0` store to `0x128D58` at the
640→1024 edge pairs with the nearest `0x8001A098` exec / `prev_pc`.
Do not change audio behavior. Do not run M5 Step 3. Do not repeat the
local missing-target `PatchesLib` build.
