# NEXT work unit (after s698: watches are not the oracle boot stall)

HYPOTHESIS-ID: m3-oracle-boot-environment

Perform one bounded, source-backed oracle launch-configuration audit. Do not
add a recovery-cell watch or alter the E9 tracer; s698 proved that the current
no-watch configuration is itself stuck at VI 320.

## Competing hypotheses

- **H-rom-identity:** the oracle ROM differs from the documented retail image;
  its checksum/region metadata will differ from the port's ROM.
- **H-core-launch-config:** the oracle's direct Core API initialization omits
  a required config/plugin setting; a source/config comparison will identify a
  concrete divergent setting from the README's previously working setup.
- **H-single-rsp-limitation:** ROM identity and launch config agree, but the
  sole installed `mupen64plus-rsp-hle` is the only executable RSP arm; no
  phase-qualified retail route exists locally until an alternate compatible
  RSP plugin is installed.

## Discriminating measurement

In one read-only batch, compare SHA-256 and N64 header bytes for the oracle
ROM and `build/rogue_squadron.z64`; enumerate all installed RSP/video/input
plugins; and trace the oracle's actual `CoreStartup`/plugin attach/config
calls against `tools/oracle/README.md`. A hash/header mismatch proves
H-rom-identity. An omitted or different concrete startup/config value proves
H-core-launch-config. Matching identity plus no alternative RSP and no
concrete config divergence supports H-single-rsp-limitation; record it and
ask a human for an alternate compatible plugin rather than treating an oracle
null as game evidence.

## Commands

    shasum -a 256 build/rogue_squadron.z64 ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64
    xxd -l 64 build/rogue_squadron.z64
    xxd -l 64 ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64
    find /opt/homebrew/lib/mupen64plus -maxdepth 1 -name 'mupen64plus-*.dylib' -print | sort
    rg -n 'CoreStartup|CoreAttachPlugin|CoreDoCommand|Config|rsp|video|audio|input' tools/oracle/rs64_oracle.c tools/oracle/README.md
