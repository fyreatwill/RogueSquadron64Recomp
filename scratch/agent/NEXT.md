# NEXT work unit — retail: menuOverlayInit entry vs jal at the 1024 edge

HYPOTHESIS-ID: m5-osvimode-menu-entry-vs-jal

Session 3281 selected `H-TickParentMenu`: the 17.0 s `runVideoFrameTick`
`prev_pc` is `menuOverlayInit` `0x800C5A18`. The port already executed
that jal once during VI 320 (s3278 `site=menu-jal`) and never again.
Iron rule 12: ask retail whether `menuOverlayInit` enters early and
waits until 17 s before the jal, or first enters at 17 s.

Do not use `--pc-phase-log-width` unless 320 origins are listed:
that flag defers `--watch-pc` until the first matching bucket
(s3281 armed at 2.3 s `640 @ 0x0066A500` and missed the port's
320-phase window).

## Competing hypotheses

- `H-MenuWaitBeforeTick`: `menuOverlayInit` entry `0x800C58A0` fires
  well before 17 s (320 or early 640); jal `0x800C5A18` is delayed
  until ~17 s. Port `slot-ret path=gate0 v0=1` skipped that wait.
- `H-LateMenuEntry`: first `0x800C58A0` exec is at ~17 s, immediately
  before the jal. Port's 320-phase `menu-entry` is the wrong-time
  invocation; missing later ENTRY is the cause.
- `H-MenuReentry`: two (or more) `0x800C58A0` entries; the 17 s jal
  belongs to a later activation the port never reaches.
- `H-EntryCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing, or neither PC fires (failed instrument / overlay-alias
  flood with no classifiable menu `prev_pc`).

## Discriminator

One retail Rice run. Exec-watch `menuOverlayInit` entry `0x800C58A0`
and jal `0x800C5A18` in the same run, armed at first VI. Printed
entry time vs 17 s jal time selects wait / late-entry / re-entry.
Classify overlay-alias hits by `prev_pc` (cinematic-resident vs
`mainGameLoop`). Boot/320 execs are coverage, not the discriminator.

Positive control: `--watch-write 0x0:0x800000` must hit (cap 10000)
AND `--vi-trace` must show title `1024 @ 0x00790400` AND `[gpr-ctl]`
/ an exec hit at `0x800C5A18` must fire (the 17 s jal is enough to
prove the watch). A silent jal watch is a failed instrument.

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
  --watch-pc 0x800C58A0,0x800C5A18 \
  --vi-trace --vi-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s3282_menu_entry_vs_jal.log 2>&1
```

No `--pc-phase-log-width`: exec watches arm on first VI (covers 320).
Join printed `0x800C58A0` times to the `0x800C5A18` 17 s jal. Lifetime
`exec-prev` still counts past EXEC_LOG_CAP 64. Do not change audio
behavior. Do not run M5 Step 3. Do not repeat the local missing-target
`PatchesLib` build.
