# NEXT work unit (retail-oracle phase ground truth for post-sec2 lead)

HYPOTHESIS-ID: m3-postsec2-lle-control

s765 landed 6w but both same-recipe port soaks crashed before the 0x1E7C /
0x1E8C reachability window. Do not rerun that repeat soak as the work unit.
Before adding another runtime instrument, use the retail oracle to establish
the independent phase timeline and positive-control write rate.

## Competing hypotheses

- **H-retail-reaches-hangar:** the retail ROM reaches the driven hangar and
  outdoor phase on the documented schedule; this makes the port's pre-window
  crash a port/runtime problem rather than an input/phase assumption.
- **H-retail-undriven-only:** without the exact verified scancode schedule the
  oracle never reaches hangar/outdoor; a null target watch would be invalid.
- **H-retail-phase-diverges:** the retail run reaches the phases, but the
  phase origins or timing differ materially; the port comparison needs a
  phase-origin gate before any new 6w conclusion.

## Discriminating measurement

One oracle run must report both: (1) whole-RDRAM positive control, with a large
write count in the first 8 emulated seconds, and (2) `--vi-trace` phase/origin
transitions through the driven 512 hangar phase and the subsequent 640 phase.
The outcomes split the hypotheses: no positive-control hits means the oracle
instrument is unusable; positive control without driven 512 means
H-retail-undriven-only; driven 512 with documented origins supports
H-retail-reaches-hangar; different origins/timing selects H-retail-phase-
diverges. Do not add a port build or interpret a null target watch in this
unit.

## Commands

    tools/oracle/build_core.sh
    tools/oracle/build.sh
    tools/oracle/build/rs64_oracle \
      --core ~/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --secs 70 --vi-trace --watch-write 0x0:0x800000 \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,\
36:start,41:start,46:start,51:start,56:start

Record the positive-control hit count, VI transitions, and origins. If the
oracle setup is unavailable, record the concrete setup error and do not
substitute a runtime-only measurement.

ORIGIN for the closed 6w change: OVL1C_1E7C jal 0x1ED4 sets r31=0x1E8C;
OVL1C_1ED4 saves $ra→$30; OVL1C_1F04 jr $30 is the legitimate return.
