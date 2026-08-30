# NEXT work unit — retail: who calls runVideoFrameTick at the 1024 edge?

HYPOTHESIS-ID: m5-osvimode-1024-tick-parent

Session 3280 selected `H-RewriteCallerPreTitle`: every post-boot
`initVideoSubsystem` entry, including the 17.2 s 1024-edge, has
`prev_pc=0x80018378` (`advanceVideoFrame`). That function has one generated
caller: `runVideoFrameTick` (`0x80001354`) jal `0x800014F0`. Four parents
call the tick. Iron rule 12: ask retail which parent is live at the
1024-edge before treating the port's single `menu-jal` as the missing one.

## Competing hypotheses

- `H-TickParentMenu`: 17.2 s `runVideoFrameTick` `prev_pc` is
  `menuOverlayInit` `0x800C5A18`. The port already reaches this jal
  (s3278 `site=menu-jal` n=1) and is missing later ticks.
- `H-TickParentMainGameLoop`: `prev_pc` is `mainGameLoop` `0x8003E29C`
  or `0x8003E360`. The 1024 rewrite is title/game-loop entry of the
  same chain, not a skipped menu tick.
- `H-TickParentMission`: `prev_pc` is `initSceneForMission` `0x800A9C70`.
  Pre-title attribution is wrong.
- `H-TickCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing, or the entry watch never fires (failed instrument).

## Discriminator

One retail Rice run. Exec-watch `runVideoFrameTick` entry `0x80001354`.
Phase-log the 17.2 s live origin so the edge print survives EXEC_LOG_CAP
64 (this function is per-frame). A printed exec at ~17.2 s with `prev_pc`
in the table above selects the matching parent. Boot/640 execs are the
watch positive control, not the discriminator.

Positive control: `--watch-write 0x0:0x800000` must hit (cap 10000) AND
`--vi-trace` must show title `1024 @ 0x00790400` AND `[gpr-ctl]` / an
exec hit at `0x80001354` must fire (a 640-phase tick is enough to prove
the watch). A silent entry watch is a failed instrument.

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
  --watch-write 0x128D58:0x128D5C \
  --watch-pc 0x80001354 \
  --detail-watch 1 \
  --pc-hist-watch 1 \
  --pc-phase-log-width 0x0066A500:640 \
  --pc-phase-log-width 0x0062BD00:640 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --pc-hist-phase 0x0066A500:640 \
  --pc-hist-phase 0x00790400:1024 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace --vi-poll \
  > scratch/agent/s3281_tick_parent.log 2>&1
```

Watch index 0 is whole-RDRAM (removed at 10000). Index 1 is the slot +8
join (`0x8001B6B0` store). Exec watch is unindexed-for-detail but prints
past cap, and `--pc-phase-log-width` forces prints at the 640-edge and
1024 origins. Join the ~17.2 s tick `prev_pc` to the 17.3 s 1024 VI
row. Do not change audio behavior. Do not run M5 Step 3. Do not repeat
the local missing-target `PatchesLib` build.
