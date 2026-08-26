# NEXT work unit (s2381) — M5 gate-writer ground truth

HYPOTHESIS-ID: m5-gate-writer-ground-truth

## Work unit

Run the M5 sequence-4 ground-truth checkpoint for gate `0x800A0F50` without
changing the port: identify retail writer PC/value transitions in title and
hangar, with the whole-RDRAM and target-phase controls in the same oracle run.
Do not promote a gate writer or consumer from a count alone.

## Competing hypotheses and discriminating measurement

- H-RetailGateWriterMatches: retail writes the gate to a nonzero value at a
  named writer PC before the target audio branch.
- H-RetailGateWriterDiffers: retail writes a different value, at a different
  PC, or in a different phase than the port's named writer.
- H-RetailGateUnobservable: the target route or positive controls do not fire,
  so no writer conclusion is valid.

The discriminator is a phase-keyed writer row containing the physical gate
write value, writer PC, target 640/title/hangar phase, and the corresponding
port writer/consumer marker. A nonzero retail store with matching phase and
named writer selects H-RetailGateWriterMatches; a positive retail store with
different source/value/ordering selects H-RetailGateWriterDiffers; missing
whole-RDRAM or target controls selects H-RetailGateUnobservable.

## Exact commands / controls

Read `tools/oracle/README.md` before changing the oracle recipe. Keep
`--watch-write 0x0:0x800000`, both target 640 origins, and add a physical
watch on `0x800A0F50:0x800A0F54` plus writer-PC histogram/detail output in the
same run. Pair it with the existing eleven-Start port driver only if the
writer/consumer markers are already present; do not alter gate behavior.

    env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --hit-cap 120 --watch-write 0x0:0x800000 --watch-write 0x800A0F50:0x800A0F54 --pc-hist-watch 1 --first-watch 1 --pc-hist-phase 0x00696100:640 --pc-hist-phase 0x00696600:640 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

Expected outcomes: the whole-RDRAM control must reach 10,000 callbacks, both
target 640 origins must appear, and the gate watch must produce a bounded
writer-PC table. Zero gate writes is unevaluable until those controls pass.
Do not change the gate, fallback, dispatch, VI, task, or audio behavior.
