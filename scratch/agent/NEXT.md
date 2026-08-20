# NEXT work unit (s2073)

HYPOTHESIS-ID: m5-a0f50-retail-value-contract

## Work unit

Capture the retail post-store value of guest gate `0x800A0F50` for each named
writer before changing any gate store. Use the existing oracle requested-PC
path and the same corrected Rice route; do not modify the port, generated gate
stores, task fields, output routing, canary, waits, guards, or defaults.

ORIGIN: the gate byte is written by legitimate retail MusyX/display-mode
functions. The oracle's post-step reader is host-side observation only; the
next test must establish the retail value contract before any guest-store arm
is attempted.

## Competing hypotheses and discriminator

- **H-RetailGateActive** — the active retail route writes `0x01` at the named
  display-mode/init writers, so the port's force-zero behavior is a guest-gate
  mismatch.
- **H-RetailGateBypass** — retail legitimately writes `0x00` at the relevant
  writer or consumer boundary, so changing that store would not explain the
  image task/exit defect.
- **H-RetailGateMixed** — retail values are writer- or phase-specific, so only
  one named store can be tested in a later arm.

The discriminator is one table with the whole-RDRAM positive control, exact
`0xA0F50` write count, one post-step value per named writer, title VI
`1024 @ 0x00790400`, and hangar VI `512 @ 0x006AB400`. All requested writer
PCs must produce a `[post-target]` row or an explicit seen=0 summary. A table
of writer hits without post-store values selects nothing.

## Exact commands

1. Before editing/building the oracle, run the existing corrected Rice witness
   with the whole-RDRAM control, exact gate watch, and both VI anchors:

   ```sh
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --hit-cap 10000 --vi-trace
   ```

2. Run one targeted gate-value arm, saving the log to a non-hidden final
   path. Require the whole-RDRAM threshold, `[post-target]` rows for
   `0x8008EA34`, `0x8008EB40`, `0x8008ED48`, `0x8008EB7C`, and `0x8008EC88`,
   and both target VI transitions:

   ```sh
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --hit-cap 10000 --vi-trace --pc-hist-watch 1 --post-value-watch 1 --post-value-pc 8008ea34,8008eb40,8008ed48,8008eb7c,8008ec88 > scratch/agent/oracle_s2073_a0f50_targeted.log 2>&1
   ```

3. Crosswalk the five values and their writer/phase timing. H-RetailGateActive
   requires a consistent nonzero active-path value; H-RetailGateBypass
   requires zero at the relevant writer; H-RetailGateMixed requires distinct
   writer/phase values. Do not land a gate change from writer ownership or
   hit counts alone.

Run `git diff --check` after the instrument change. No game binary build or
guest behavior change is authorized by this work unit.
