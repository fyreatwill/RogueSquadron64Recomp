# NEXT work unit (long oracle debugger-mode phase A/B)

HYPOTHESIS-ID: oracle-320-only-divergence

s772 showed the debugger-on arm's positive control and initial VI trace, while
debugger-off `--vi-poll` observed the same initial width/origin but cannot
report debugger-callback VI totals. The next unit is one bounded long phase
check using the documented 11-entry Start schedule and fresh configs.

## Competing hypotheses

- H-oracle-debugger-interference: debugger callbacks or interpreter overhead
  change the retail phase path; the long arms will show different width/origin
  transitions.
- H-oracle-rom-runtime-divergence: debugger mode does not affect the result;
  both long arms will show the same phase transitions.
- H-oracle-poll-observation: debugger-off polling is insufficient for the
  later phase; debugger-on has a positive control but debugger-off cannot
  produce a trustworthy comparable transition record.

## Discriminating measurement

Run matched 70-second arms with the same ROM/core and fresh config directories:
debugger-on with `--press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --oracle-debugger 1 --vi-trace --pif-trace --watch-write 0x0:0x800000`, and debugger-off with the same schedule plus `--oracle-debugger 0 --vi-poll`. The debugger-on arm must pass the positive control and log the scheduled inputs. A difference in width/origin transitions selects H-oracle-debugger-interference; identical transitions select H-oracle-rom-runtime-divergence; a debugger-off poll that cannot record later transitions is unevaluable and selects H-oracle-poll-observation only if the debugger-on control is positive.

## Commands

   rm -rf /tmp/rs64-oracle-config-s773-a /tmp/rs64-oracle-config-s773-b scratch/agent/oracle-config-s773 && mkdir -p /tmp/rs64-oracle-config-s773-a /tmp/rs64-oracle-config-s773-b scratch/agent/oracle-config-s773
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s773-a --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --oracle-debugger 1 --vi-trace --pif-trace --watch-write 0x0:0x800000 > scratch/agent/oracle-config-s773/a.log 2>&1 & p1=$!
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s773-b --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --oracle-debugger 0 --vi-poll > scratch/agent/oracle-config-s773/b.log 2>&1 & p2=$!
   wait "$p1"; r1=$?; wait "$p2"; r2=$?; printf 'a_rc=%s b_rc=%s\n' "$r1" "$r2"
