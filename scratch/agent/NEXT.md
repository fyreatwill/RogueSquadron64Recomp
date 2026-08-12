# NEXT work unit (after s704: isolate the oracle debugger/interpreter launch mode)

HYPOTHESIS-ID: m3-oracle-boot-environment

Do not add a target watch or alter the E9 tracer beforehand. Make one bounded,
regeneration-independent oracle change: expose the existing forced
`EnableDebugger=1` and `R4300Emulator=0` settings as CLI-selectable launch
arms, preserving the present debugger/pure-interpreter defaults.

## Competing hypotheses

- **H-debugger-route:** `EnableDebugger=1` causes the VI-320 stall; a
  debugger-off arm reaches 640/1024/0x6ABxxx under the documented schedule.
- **H-interpreter-route:** pure interpreter (`R4300Emulator=0`) causes the
  stall; a nonzero emulator-mode arm reaches those phases while debugger state
  is held constant.
- **H-core-environment-route:** every arm remains at 320 despite PIF and
  whole-RDRAM controls; the residual is elsewhere in the oracle core/data path.

## Discriminating measurement

Run the debugger-off, alternate-emulator-mode, and default arms concurrently
with identical retail ROM, current RSP HLE, `--vi-trace`, `--pif-trace`, the
eleven Starts at 6..56 s, and a whole-RDRAM control wherever debugger support
permits it. If debugger-off alone progresses, H-debugger-route wins. If only
the nonzero emulator-mode arm progresses, H-interpreter-route wins. If all
phase-stall with live PIF controls (and live write controls in debugger arms),
H-core-environment-route remains; keep target-watch zeros unqualified.

## Commands (after adding the CLI launch-mode switches)

    tools/oracle/build.sh
    # launch all three arms concurrently; use separate --configdir paths
    tools/oracle/build/rs64_oracle --rom build/rogue_squadron.z64 --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace --pif-trace --watch-write 0:0x800000
    tools/oracle/build/rs64_oracle --rom build/rogue_squadron.z64 --oracle-debugger 0 --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace --pif-trace
    tools/oracle/build/rs64_oracle --rom build/rogue_squadron.z64 --oracle-emulator 1 --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace --pif-trace --watch-write 0:0x800000
