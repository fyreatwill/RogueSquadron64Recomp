# Session 3055 — VI-mode stall oracle setup audit

## Planned discriminator

Compare a retail oracle run with a port AUTOPILOT run: retail must show the
caller and width for the 640-to-1024 VI transition, while the port must show
whether that caller and width occur.

## Port arm

The 90-second LLE-only AUTOPILOT capture ran from `build/` with the ROM
present. It produced 29,390 log lines and stayed at VI 640, origin
`0x0066A500`, after the initial transitions. The four unconditional
`osViSetMode` records were:

| call | width | site |
|---:|---:|---|
| 1 | 320 | `initVideoSubsystem` |
| 2 | 2 | `swapBufferWithViMode` |
| 3 | 640 | `initVideoSubsystem` |
| 4 | 640 | `applyPendingViChanges` |

There were zero `width=1024` records and no title/hangar phase. This is a
positive port logging result, but it cannot distinguish whether retail uses a
different caller or whether the port never reaches that caller.

## Oracle arm and controls

The first command used the documented `--positive-rdram` option and exited
with rc 2 because this checkout's frontend does not implement that option.
The fixed command removed it and added the supported whole-RDRAM watch
`--watch-write 0x0:0x800000` alongside the VI-register watch. It exited rc 1
before emulation:

`dlopen(/opt/homebrew/lib/mupen64plus/libmupen64plus.dylib): ... no such file`

The debugger-enabled mupen core and Rice plugin were also absent from the
searched local Homebrew and workspace paths. Therefore no retail VI trace or
positive-control hit occurred. This is a setup failure, not a retail null.

## Result

The planned three-way discriminator did not run. The port arm reproduces the
pre-title VI-640 boundary, while the independent retail arm is blocked by a
missing debugger-enabled mupen core (and Rice plugin). No hypothesis is
selected and no runtime behavior changed.

Evidence files: `/tmp/port_osvisetmode.log` and
`/tmp/retail_osvisetmode_fixed.log`.
