# NEXT work unit (oracle effective-config divergence check)

HYPOTHESIS-ID: oracle-320-only-divergence

s770 completed the undriven-versus-driven A/B: both arms passed the positive
control and remained at VI 320, so input-induced 320 is refuted. The next unit
is one bounded configuration-focused oracle check that materializes fresh
config/plugin state in two identical arms and compares it with the documented
defaults before another phase run.

## Competing hypotheses

- H-oracle-plugin-default: the fresh configs select a plugin/core default that
  keeps the retail run at the 320 framebuffer path.
- H-oracle-rom-runtime-divergence: the retail ROM/core pair itself differs from
  the source of the documented phase timeline despite matching SHA-256.
- H-oracle-config-generation: generated config contents differ between the
  fresh arm and the sibling known-good setup and explain the phase null.

## Discriminating measurement

Materialize two fresh configs with the same oracle binary, diff their
`mupen64plus.cfg` files, and record plugin/core/default entries against the
defaults documented in `tools/oracle/README.md`. Then run one 15-second
undriven positive-control check from the audited config. A config/plugin
difference plus a later VI phase selects
H-oracle-config-generation or H-oracle-plugin-default; identical effective
settings plus VI 320 selects H-oracle-rom-runtime-divergence. Missing control
hits make the run unevaluable.

## Commands

    rm -rf /tmp/rs64-oracle-config-s771-a /tmp/rs64-oracle-config-s771-b
    mkdir -p /tmp/rs64-oracle-config-s771-a /tmp/rs64-oracle-config-s771-b scratch/agent/oracle-config-s771
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s771-a --secs 15 --vi-trace --watch-write 0x0:0x800000 > scratch/agent/oracle-config-s771/a.log 2>&1 & p1=$!
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s771-b --secs 15 --vi-trace --watch-write 0x0:0x800000 > scratch/agent/oracle-config-s771/b.log 2>&1 & p2=$!
    wait "$p1"; r1=$?; wait "$p2"; r2=$?; printf 'a_rc=%s b_rc=%s\n' "$r1" "$r2"
    diff -u /tmp/rs64-oracle-config-s771-a/mupen64plus.cfg /tmp/rs64-oracle-config-s771-b/mupen64plus.cfg || true
    grep -n 'Video-\|Core\|Input-SDL\|Start\|Plugin' /tmp/rs64-oracle-config-s771-a/mupen64plus.cfg

Use `grep -n`/`tail` on the bounded result log; do not cat it. Record config
differences, positive-control hits, and VI transitions in the next ledger entry.
