# NEXT work unit (after s705: give debugger-off oracle runs an independent phase witness)

HYPOTHESIS-ID: m3-oracle-boot-environment

Do not add a target watch or alter the E9 tracer. Make one bounded,
regeneration-independent oracle change: add a `--vi-poll` path which reads the
VI width/origin registers through the core API outside debugger callbacks and
prints an initial sample plus every change. Keep the existing callback trace
unchanged for its debugger-on positive control.

## Competing hypotheses

- **H-debugger-route:** debugger-off direct VI polling reaches 640/1024/0x6ABxxx
  while debugger-on remains 320.
- **H-core-environment-route:** direct polling reports the initial 320 control
  but never a phase transition in debugger-off, debugger-on, or emulator=1.
- **H-poll-unavailable:** the non-callback read API cannot obtain the initial
  width in debugger-off; the arm is explicitly uninstrumented, so neither
  route hypothesis is tested and the next lead is an external/video-plugin
  phase witness.

## Discriminating measurement

The positive control is a visible initial `--vi-poll` width=320 sample in each
arm; default must also match its existing `[vi] WIDTH 0 -> 320` callback line.
Run debugger-off, default, and emulator=1 concurrently with identical retail
ROM/current RSP HLE, eleven Starts at 6..56 seconds, and separate config
directories. Default/emulator retain `--pif-trace`, `--vi-trace`, and
`--watch-write 0:0x800000`. A debugger-off 640/1024/0x6ABxxx result confirms
H-debugger-route; live 320-only polling in all arms refutes it and supports
H-core-environment-route; no debugger-off initial sample confirms
H-poll-unavailable instead.

## Commands (after adding `--vi-poll`)

    tools/oracle/build.sh
    # Launch all three arms concurrently with the explicit DEBUGGER=1 core path.
    # Use the s705 press schedule, separate configs, and capture logs under
    # scratch/agent/s706_oracle_vi_poll/.
