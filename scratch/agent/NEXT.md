# NEXT work unit (oracle undriven-versus-driven phase A/B)

HYPOTHESIS-ID: oracle-320-only-divergence

s769 matched ROM identity, fresh config, PIF Start delivery, and the
whole-RDRAM positive control, yet remained at VI 320. The next unit is one
same-iteration A/B: run undriven and driven arms with separate fresh config
directories and identical oracle/core settings.

## Competing hypotheses

- H-oracle-input-induced-320: the injected Start schedule changes the retail
  state path in this current core/config, so undriven reaches a later VI phase
  while driven remains at 320.
- H-oracle-environment-320: both arms remain at 320, so the documented phase
  timeline is not reproducible in this oracle environment despite correct ROM,
  execution, and input delivery.
- H-oracle-config-arm: only one fresh-config arm differs, indicating a
  per-run config/plugin initialization effect rather than game behavior.

## Discriminating measurement

Record ROM SHA-256 once, then run both arms with `--vi-trace`, `--pif-trace`,
and `--watch-write 0x0:0x800000`. The undriven arm has no `--press`; the
driven arm uses all eleven documented Start presses. The whole-RDRAM watch
must fire in both arms. Undriven reaching 640/1024/512 while driven stays 320
selects H-oracle-input-induced-320. Both arms staying at 320 selects
H-oracle-environment-320. A difference in config creation or missing positive
control makes that arm unevaluable and selects H-oracle-config-arm for a
config-focused follow-up; do not interpret a null without its control.

## Commands

    shasum -a 256 /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
    rm -rf /tmp/rs64-oracle-config-undriven /tmp/rs64-oracle-config-driven
    mkdir -p /tmp/rs64-oracle-config-undriven /tmp/rs64-oracle-config-driven scratch/agent/oracle-ab-s770
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-undriven --secs 70 --pif-trace --vi-trace --watch-write 0x0:0x800000 > scratch/agent/oracle-ab-s770/undriven.log 2>&1 &
    p1=$!
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-driven --secs 70 --pif-trace --vi-trace --watch-write 0x0:0x800000 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/oracle-ab-s770/driven.log 2>&1 &
    p2=$!
    wait "$p1"; r1=$?
    wait "$p2"; r2=$?
    printf 'undriven_rc=%s driven_rc=%s\n' "$r1" "$r2"

Use `grep -n`/`tail` on the two bounded result logs; do not cat them.
Positive-control hit counts, PIF words, VI transitions, config paths, and ROM
hash go into the next ledger entry.
