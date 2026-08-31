# NEXT work unit — attribute the retail indirect-pointer writer

HYPOTHESIS-ID: m5-callback-indirect-pointer-source

Session 3343 made the port writer probe target-valid: its aggregate arm passed
host/task/title/hangar controls and recorded five target-phase writes at
`0x80091900 -> 0x80007910`, plus `0x80007928 -> 0x8009123C`. Retail ground
truth recorded one write at the corrected physical slot `0x001499D4` with the
whole-RDRAM control active.

Competing hypotheses:

- `H-PointerWriter`: retail writes the indirect pointer in the target route.
- `H-StalePointer`: retail never writes it in the target route; the port's
  target-phase initializer store is a port-specific stale/early population.
- `H-HostDispatch`: neither guest writer is responsible; a host/runtime path
  supplies the effective callback.

The discriminating measurement is one retail oracle run with a whole-RDRAM
positive control, Rice video, the documented Start schedule, and
`--watch-write 0x1499d4:0x1499d8 --pc-hist-watch 1`, long enough to reach title
1024 and hangar 512. A target-phase hit and writer-PC histogram supports
`H-PointerWriter`; a valid target run with no corrected-slot hit, alongside
the already captured port writer, supports `H-StalePointer`; a valid run with
the slot hit absent and a matching indirect execution but no guest writer
keeps `H-HostDispatch` live. A missing title/hangar control or whole-RDRAM
control invalidates the null. No behavior change is authorized.

Exact command:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x1499d4:0x1499d8 --pc-hist-watch 1 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
