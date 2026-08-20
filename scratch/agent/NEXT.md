# NEXT work unit (s2014) — capture retail MusyX gate writers

HYPOTHESIS-ID: m5-retail-gate-ground-truth

## Work unit

Capture independent retail ground truth for the MusyX enabled-state byte before
adding port instrumentation. First run the whole-RDRAM positive control, then
run the debugger-on Rice recipe with a narrow watch on physical `0xA0F50`
(`0x800A0F50`). Do not rebuild, reconcile, or edit the generated/symbol trees,
and do not change any runtime audio, status, spin, PI, or mitigation behavior.

## Competing hypotheses and discriminator

- H1: The retail gate is written by the named init/display/shutdown paths; the
  target watch reports their PCs and the expected zero/nonzero transitions.
- H2: The gate is not written in the debugger-on prefix despite a valid oracle
  watch; this leaves the retail gate contract unattributed and selects a
  phase/driver reachability question rather than a port-side explanation.
- H3: The oracle's watch is invalid or the run does not reach its expected
  phase; a failed whole-RDRAM control or missing phase evidence makes the
  target result unevaluable.

The discriminator is positive-control hit volume followed by target-watch hit
records containing the retail PC, old/new value, and phase. The positive
control must produce roughly 1.6M whole-RDRAM writes in 8 emulated seconds;
only then is a target-watch null meaningful. H1 is selected by named-PC
transitions; H2 requires a valid control and phase reach without target hits;
H3 is selected by either failed control or absent phase reach.

## Exact commands

Build the frontend, then run the positive control:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --oracle-debugger 1 --oracle-emulator 1 --secs 8 \
  --watch-write 0x0:0x800000 \
  > scratch/agent/s2014-oracle-rdram-control.log 2>&1
```

The target run uses the eleven-Start Rice schedule and watches the aligned
word containing the gate:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --oracle-debugger 1 --oracle-emulator 1 --secs 60 \
  --vi-trace \
  --watch-write 0xA0F50:0xA0F54 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2014-oracle-gate-watch.log 2>&1
```

Expected H1 PCs are the retail writers corresponding to `initMusyXEngine`,
`setDisplayMode`, `reapplyDisplayMode`, and shutdown/failure zeroing. A valid
positive control followed by no target hit is not enough to claim H2 unless
the target run also reports the relevant boot/title phase; a debugger-on stall
before that phase selects H3. Do not infer the port-side thread join from this
watch, promote audio, alter status/spin/PI behavior, or weaken a guard.
