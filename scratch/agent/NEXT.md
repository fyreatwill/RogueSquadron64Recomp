# NEXT work unit (oracle debugger instrumentation phase check)

HYPOTHESIS-ID: oracle-320-only-divergence

s771 completed the fresh-config A/B: both arms materialized byte-identical
configs, passed the positive control, and remained at VI 320. The next unit is
one bounded debugger-mode check using the same ROM/core and a fresh config.

## Competing hypotheses

- H-oracle-debugger-interference: debugger callbacks or interpreter overhead
  change the retail phase path; debugger-on and debugger-off will diverge.
- H-oracle-rom-runtime-divergence: debugger mode does not affect the result;
  both arms remain at width 320 with the same origin behavior.
- H-oracle-poll-observation: `--vi-poll` is insufficient or observes a
  different register path; debugger-off produces no trustworthy VI result.

## Discriminating measurement

Run matched short arms with `--oracle-debugger 1 --vi-trace` and
`--oracle-debugger 0 --vi-poll`, using the same ROM/core and fresh config
directories. The debugger-on arm must have whole-RDRAM positive-control hits;
the debugger-off arm must report a nonzero VI poll. A phase difference selects
H-oracle-debugger-interference; identical width-320/origin behavior selects
H-oracle-rom-runtime-divergence; a missing poll is unevaluable and selects
H-oracle-poll-observation only if the debugger-on control is positive.

## Commands

   rm -rf /tmp/rs64-oracle-config-s772-a /tmp/rs64-oracle-config-s772-b
   mkdir -p /tmp/rs64-oracle-config-s772-a /tmp/rs64-oracle-config-s772-b scratch/agent/oracle-config-s772
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s772-a --secs 15 --oracle-debugger 1 --vi-trace --watch-write 0x0:0x800000 > scratch/agent/oracle-config-s772/a.log 2>&1 & p1=$!
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s772-b --secs 15 --oracle-debugger 0 --vi-poll > scratch/agent/oracle-config-s772/b.log 2>&1 & p2=$!
   wait "$p1"; r1=$?; wait "$p2"; r2=$?; printf 'a_rc=%s b_rc=%s\n' "$r1" "$r2"
   diff -u /tmp/rs64-oracle-config-s771-a/mupen64plus.cfg /tmp/rs64-oracle-config-s771-b/mupen64plus.cfg || true
   grep -n 'Video-\|Core\|Input-SDL\|Start\|Plugin' /tmp/rs64-oracle-config-s771-a/mupen64plus.cfg
    rm -rf /tmp/rs64-oracle-config-s772-a /tmp/rs64-oracle-config-s772-b
    mkdir -p /tmp/rs64-oracle-config-s772-a /tmp/rs64-oracle-config-s772-b scratch/agent/oracle-config-s772
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s772-a --secs 15 --oracle-debugger 1 --vi-trace --watch-write 0x0:0x800000 > scratch/agent/oracle-config-s772/a.log 2>&1 & p1=$!
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s772-b --secs 15 --oracle-debugger 0 --vi-poll > scratch/agent/oracle-config-s772/b.log 2>&1 & p2=$!
    wait "$p1"; r1=$?; wait "$p2"; r2=$?; printf 'a_rc=%s b_rc=%s\n' "$r1" "$r2"

Use `grep -n`/`tail` on the bounded result logs; do not cat them. Record each
arm's positive-control status and VI transitions in the next ledger entry.
