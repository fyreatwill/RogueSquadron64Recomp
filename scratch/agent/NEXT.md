# NEXT work unit (oracle input-only phase A/B)

HYPOTHESIS-ID: oracle-input-phase-divergence

The s780 two-arm 130-second driven recipe stayed at width 320/origin
`0x6dd280`, with 21,635,499 whole-RDRAM positive-control writes, 7,799 VI
callbacks, and all eleven Start presses in each arm. A transition is not merely
late in that recipe. The next work unit compares it with the documented
later-phase-driving undriven recipe while holding core, emulator, ROM, duration,
and instrumentation constant.

## Competing hypotheses

- H-input-conditioned-phase: removing the eleven Start presses allows the
  documented later 102-second attract-demo phase (512 at origin `0x690800`).
- H-runtime-or-rom-discrepancy: both recipes remain 320-only despite the
  documented difference, so input schedule alone does not explain the retail
  timeline.

## Discriminating measurement

Run two concurrent debugger-on, emulator-1 arms for 130 seconds. Arm A uses no
`--press`; arm B uses the eleven-entry Start schedule. Both must use
`--watch-write 0x0:0x800000`, `--vi-trace`, and `--pif-trace`. A 512/1024/640
transition only in arm A selects H-input-conditioned-phase. Identical 320-only
VI traces with positive controls in both arms select H-runtime-or-rom-
discrepancy. The whole-RDRAM watch and the PIF/press records are positive
controls; a zero phase-transition result is not evaluable without them.

## Commands

Use `tools/oracle/build/rs64_oracle` with the verified core and retail ROM:

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 130 --oracle-debugger 1 --oracle-emulator 1 --watch-write 0x0:0x800000 --vi-trace --pif-trace
```

Run that command concurrently once without `--press` and once with:

```text
--press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150
```

Store logs under `scratch/agent/oracle_runs/20260814_input_phase/` and kill
with SIGKILL only if an external timeout is required.
