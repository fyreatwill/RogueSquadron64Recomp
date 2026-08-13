# NEXT work unit (oracle runtime/config identity audit)

HYPOTHESIS-ID: oracle-runtime-identity-divergence

s774 proved debugger-off raw VI observation is live: 70 samples stayed at
width 320/origin `0x6dd280`, while debugger-on independently reached 4,199 VI
with the same phase. The next unit is one bounded, read-only identity audit of
the retail oracle environment before any new instrument or port-side inference.

## Competing hypotheses

- H-oracle-core-build-drift: the loaded core or its build options differ from
  the documented/debugger-enabled core used to establish the phase timeline.
- H-oracle-plugin-drift: the effective attached plugin binaries or materialized
  config differ from the expected headless setup in a way that holds the game at
  width 320.
- H-oracle-rom-oracle-drift: core/plugin/config identity matches, leaving the
  ROM/oracle runtime behavior itself as the remaining explanation.

## Discriminating measurement

Collect SHA-256 and file metadata for the loaded core, oracle executable, RSP,
input, and ROM in both existing s774 config arms; diff the two materialized
configs and extract their plugin paths and debugger/emulator settings. A
byte/config mismatch selects core-build or plugin drift; identical identities
with the positive-control/PIF/VI result selects oracle-runtime/ROM divergence.

## Commands

    shasum -a 256 tools/oracle/build/rs64_oracle /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib /opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib /opt/homebrew/lib/mupen64plus/mupen64plus-input-sdl.dylib /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 > scratch/agent/oracle-config-s774/identity.sha256
    diff -u /tmp/rs64-oracle-config-s774-a/mupen64plus.cfg /tmp/rs64-oracle-config-s774-b/mupen64plus.cfg > scratch/agent/oracle-config-s774/config.diff || true
    rg -n "(Core/EnableDebugger|Core/R4300Emulator|Video-Plugin|Audio-Plugin|Input-Plugin|RSP-Plugin|Plugin)" /tmp/rs64-oracle-config-s774-a/mupen64plus.cfg /tmp/rs64-oracle-config-s774-b/mupen64plus.cfg > scratch/agent/oracle-config-s774/config-identity.txt
