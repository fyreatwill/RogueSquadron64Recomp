# NEXT work unit (oracle input-plugin attachment A/B)

HYPOTHESIS-ID: oracle-input-plugin-state

The s781 130-second A/B held both no-press and eleven-Start arms at width
320/origin `0x6dd280`, despite positive whole-RDRAM watches; the driven arm
also logged all eleven PIF presses. Input schedule alone is therefore not the
documented phase discriminator. The remaining recipe difference is that the
no-press command did not attach input-SDL, while the driven command did.

## Competing hypotheses

- H-input-plugin-state: attaching the verified input-SDL plugin, even with no
  presses, allows the documented later 512 attract-demo phase.
- H-runtime-or-rom-discrepancy: both no-press arms remain 320-only, so plugin
  attachment does not explain the retail timeline.

## Discriminating measurement

Run two concurrent debugger-on, emulator-1 arms for 130 seconds. Both use no
`--press`, `--watch-write 0x0:0x800000`, `--vi-trace`, and `--pif-trace`; only
arm B adds the verified input plugin. A 512/1024/640 transition only in arm B
selects H-input-plugin-state. Identical 320-only VI traces with positive
whole-RDRAM writes in both arms select H-runtime-or-rom-discrepancy. Do not
interpret missing callbacks as a null: the whole-RDRAM watch must fire in both
arms.

## Commands

Use the verified core and retail ROM. Store logs under
`scratch/agent/oracle_runs/20260813_input_plugin/` and kill with SIGKILL only
if an external timeout is required.

Arm A (no input plugin):

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 130 --oracle-debugger 1 --oracle-emulator 1 --watch-write 0x0:0x800000 --vi-trace --pif-trace
```

Arm B adds:

```text
--input /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-input-sdl.dylib
```
