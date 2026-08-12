# Blocked: alternate Mupen64Plus RSP plugin required

Need: a path to an alternate Mupen64Plus-compatible RSP plugin for macOS
(`.dylib`) that can be loaded by the local Mupen64Plus 2.6.0 core.

Why: the active oracle work unit requires current and alternate RSP arms in
the same 70-second driven positive-control batch. Only a differing result can
separate H-rsp-hle-route from H-core-environment-route.

Tried this iteration: `find /opt/homebrew /usr/local -type f` for RSP dylibs
and shared objects. It found only the already-tested
`mupen64plus-rsp-hle.dylib`. The current truth records that ROM identity,
launch configuration, PIF input, and whole-RDRAM watch controls have already
been checked; another one-arm run is unqualified.

After supply: set its path in the two commands in `scratch/agent/NEXT.md` and
run the alternate and current RSP arms with the identical retail ROM, eleven
Start schedule, VI/PIF traces, and whole-RDRAM write control.
