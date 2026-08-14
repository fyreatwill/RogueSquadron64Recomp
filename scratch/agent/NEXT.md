# NEXT work unit (s1036)

HYPOTHESIS-ID: retail-oracle-config-initialization

Perform one bounded source/config audit of the retail oracle, then make the
smallest config-initialization fix if the cause is local and rerun its
documented phase schedule. Do not change the recomp runtime or arm the
freelist watch.

## Competing hypotheses and discriminator

* `H-config-order`: CoreStartup reads the config before the front-end creates
  or versions the Input-SDL sections; fixing initialization removes the
  warning and preserves the verified mapping.
* `H-plugin-defaults`: the warning is harmless because the attached input
  plugin uses its own defaults; a clean config run still remains at width
  320/origin `0x006dd280`.
* `H-phase-path`: configuration is clean and the documented 11-Start schedule
  still reaches no 512 phase, so the README timeline belongs to another
  environment or an unobserved transition.

Discriminating measurement: inspect the order of `CoreStartup`, config-section
creation/versioning, and input-plugin attachment in `tools/oracle/rs64_oracle.c`.
Then run one 60-second arm with the whole-RDRAM watch removed at 10,000
callbacks, `[pad]` and VI traces, and the documented 11-Start schedule.
Missing input-section warnings after the fix select `H-config-order`; clean
startup plus the same width-320/origin path selects `H-plugin-defaults` or
`H-phase-path` according to whether the plugin reports defaults versus an
explicit configured mapping. Missing positive control invalidates the run.

## Exact command

```sh
mkdir -p /tmp/rs64-oracle-s1036
shasum -a 256 rogue_squadron.z64 > scratch/agent/oracle_s1036_rom_hash.txt
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/rogue_squadron.z64 \
  --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --datadir /opt/homebrew/share/mupen64plus \
  --configdir /tmp/rs64-oracle-s1036 \
  --secs 60 \
  --watch-write 0x0:0x800000 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --hold-ms 150 --vi-trace --pif-trace \
  > scratch/agent/oracle_s1036_capture.log 2>&1
```

Before running, inspect the config/attachment order and patch only if the
warning is caused by local ordering. Verify the generated config maps
`Start = "key(40)"` before interpreting input. The whole-RDRAM watch must be
removed at the validated threshold and is not a target; do not interpret a
freelist null until a 512 hangar-origin phase is reached.
