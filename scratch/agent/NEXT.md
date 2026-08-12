# NEXT work unit (after s702: alternate RSP required for a phase-qualified oracle)

HYPOTHESIS-ID: m3-oracle-boot-environment

Blocked pending a human-provided alternate compatible Mupen64Plus RSP plugin.
The only installed implementation is Homebrew `mupen64plus-rsp-hle`; s699
refuted ROM-identity and checked launch-config drift, and the fresh s702
inventory again found no alternate plugin. Do not add a target watch or alter
the E9 tracer beforehand.

## Competing hypotheses

- **H-rsp-hle-route:** the current RSP HLE path causes the VI-320 stall; an
  alternate RSP reaches 640/1024/hangar under the documented driven schedule.
- **H-core-environment-route:** an alternate RSP also remains at 320 despite
  PIF and whole-RDRAM controls; the residual lies in the debugger/core launch
  environment, not the RSP implementation.

## Discriminating measurement

Run both RSP arms in one batch with identical retail ROM, `--vi-trace`,
`--pif-trace`, eleven Starts at 6..56 s, and the whole-RDRAM write control.
If only the alternate reaches a 640/1024/0x6ABxxx phase, H-rsp-hle-route wins
and a subsequent narrow recovery-cell watch is qualified. If both remain at
320 while both controls fire, H-core-environment-route wins; keep oracle
target-watch zeros unqualified and audit the debugger/core build next.

## Commands (after the human supplies `ALT_RSP_PATH`)

    tools/oracle/build.sh
    tools/oracle/rs64_oracle --rom build/rogue_squadron.z64 --rsp /path/to/alternate-rsp.dylib --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace --pif-trace --watch-write 0:0x800000
    tools/oracle/rs64_oracle --rom build/rogue_squadron.z64 --rsp /opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace --pif-trace --watch-write 0:0x800000
