# NEXT work unit — port fade-out path vs retail 6.1–6.6 s 2B84 window

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3287 selects `H-DelaySlotWatchMiss`: retail's first
`menuOverlayInit` leaves `runMenuModelViewerScreen` because the
`$s2==2` fade-out path (`L_800C2B00`) runs at 6.1–6.6 s, the last
`0x800C2B84` (`bc1tl $f24==0`) is taken (delay slot sets `$s5=1`),
and `0x800C2D50` (`beq $s5,$v0` with `$v0=1`) jumps to `L_800C2DA0`.
Mupen does not report `0x800C2B88`. The port (s3278) entered this
screen at `640 @ 0x66A500` and never reached the slot tail.

Host recomp executes the delay slot in the `if (c1cs)` body, so a
taken `0x800C2B84` on the port WOULD set `$s5=1` and the next `2D50`
would exit. The stuck port is therefore a fade-out / `$f24` problem,
not an oracle delay-slot artifact.

## Competing hypotheses

- `H-PortFadeOutNeverEntered`: during the 640 viewer hold, `L_800C2B00`
  and `0x800C2B84` stay silent while `0x800C2D50` keeps falling through
  (`$s5!=1`). `$s2` never becomes 2.
- `H-PortF24NeverZero`: `0x800C2B00` / `0x800C2B84` fire, but `c1cs`
  stays false (`$f24!=0`) and `0x800C2D50` never takes.
- `H-PortS5Lost`: `0x800C2B84` is taken (`$s5=1`) and `0x800C2D50`
  still falls through.
- `H-PortTailReached`: `0x800C2DA0` / return fire (s3278 stale).
- `H-PortCoverageInvalid`: existing `[m5-postwait]` viewer entry silent,
  or `[phase]` never reaches 640.

## Discriminator

One Debug rebuild with a fixup probe at `L_800C2B00`, `0x800C2B84`
(log `c1cs`, `$s5`/`r21`, `$s2`/`r18`, `$f24` bits), and the taken
arm of `0x800C2D50`. One 30 s port run from `build/` with the ROM
present. Positive control: s2045 `[m5-postwait]` viewer `entry` must
fire (enable `ROGUESQ_LOG_M5_POSTWAIT=1`) AND `[phase]` 640 at
`0x0066A500`. Rate-limit 2B00/2B84 to first 10 + every 50.

Silent 2B00+2B84 with live 2D50 fallthrough selects
`H-PortFadeOutNeverEntered`. 2B84 with `c1cs=0` throughout selects
`H-PortF24NeverZero`. Taken 2B84 then still-falling 2D50 selects
`H-PortS5Lost`. 2DA0/return selects `H-PortTailReached`. Silent
entry or no 640 phase is a failed instrument.

Do not add a skip, allow, restore, or wait bypass. No M5 Step 3.

## Exact commands

```sh
python3 tools/apply_s3288_viewer_fade_probe.py
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Then from `build/`, 30 s, SIGKILL, `ROGUESQ_LOG_M5_POSTWAIT=1` plus
existing `[phase]` / `[slot-ret-caller]` (unconditional). Log:
`scratch/agent/s3288_port_viewer_fade.log`.
