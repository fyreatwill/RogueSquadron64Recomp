# NEXT work unit (s1037)

HYPOTHESIS-ID: retail-oracle-phase-path

Perform one bounded phase-path audit of the retail oracle and one phase-gated
run using the already verified input path. Do not change the recomp runtime or
arm the freelist watch.

## Competing hypotheses and discriminator

* `H-phase-transition`: the retail/core setup has a deterministic transition
  condition not met by the nominal 11-Start wall-clock schedule; a phase-gated
  or input-held schedule produces a VI width/origin transition beyond 320.
* `H-retail-attract`: Start is consumed, but this ROM/core/plugin combination
  remains in an attract path whose later transition is not caused by Start; the
  phase-gated run stays at width 320/origin `0x006dd280` with positive pad
  controls.
* `H-vi-observation`: the game changes state but the VI callback/read path
  misses the relevant transition; an independent VI poll or core trace shows a
  width/origin change absent from the callback trace.

Discriminating measurement: audit the retail input/VI transition code and run
one 60-second arm with `--hit-cap 10000`, whole-RDRAM positive control,
`--vi-trace --vi-poll --pif-trace`, and a phase-gated schedule whose controls
are keyed to observed VI transitions rather than wall-clock assumptions.
Positive control and pad edges must fire. A width/origin transition in the
poller or callback selects `H-phase-transition` or `H-vi-observation`; no
transition with positive controls selects `H-retail-attract`.

## Exact commands

```sh
rg -n "M64CMD_SEND_SDL|press|dbg_vi|VI_WIDTH|VI_ORIGIN" tools/oracle/rs64_oracle.c /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src
mkdir -p /tmp/rs64-oracle-s1037
shasum -a 256 rogue_squadron.z64 > scratch/agent/oracle_s1037_rom_hash.txt
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/rogue_squadron.z64 \
  --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --datadir /opt/homebrew/share/mupen64plus \
  --configdir /tmp/rs64-oracle-s1037 \
  --secs 60 \
  --hit-cap 10000 --watch-write 0x0:0x800000 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --hold-ms 150 --vi-trace --vi-poll --pif-trace \
  > scratch/agent/oracle_s1037_capture.log 2>&1
```

The whole-RDRAM watch must be removed at the validated threshold and is not a
target. Do not interpret a freelist null until a 512 hangar-origin phase is
reached. If the phase-gated schedule cannot be implemented without a source
change, stop before building and record the exact missing transition signal.
