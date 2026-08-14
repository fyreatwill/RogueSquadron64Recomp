# NEXT work unit (s1113)

HYPOTHESIS-ID: submit-phase-route-audit

Build the debugger-enabled retail-oracle core, the next ranked step after the
s1112 lifecycle audit. Do not run a game capture until the core and front-end
positive controls are both available.

Competing hypotheses:

* H-oracle-core: `build_core.sh` produces a debugger-enabled core dylib and the
  existing front end can load it.
* H-build-env: the source/toolchain or Homebrew dependency is the blocker.
* H-front-end-mismatch: the core builds, but the front end rejects it or its
  debugger symbols/configuration are unusable.

Discriminator: `build_core.sh` exit/status plus a front-end setup check using
`tools/oracle/build/rs64_oracle --core <built-dylib> --rom ... --secs 8
--watch-write 0:0x800000`. A successful build and approximately 1.6M whole-
RDRAM callbacks select H-oracle-core; a build failure selects H-build-env; a
built dylib rejected by the front end selects H-front-end-mismatch. Do not
interpret target-watch zeros until the whole-RDRAM control fires.

Exact commands:

```sh
tools/oracle/build_core.sh
tools/oracle/build.sh
find /Users/williambuckley/Documents/Tools -name 'libmupen64plus.dylib' -type f -print
tools/oracle/build/rs64_oracle --help
```

If the core builds, run only the 8-second whole-RDRAM positive-control setup
check, capturing output under `scratch/agent/oracle_core_check/`. No port build,
mode-state watch, mitigation, or soak is authorized for this unit.
