# NEXT work unit (s2287) — retail ground-truth route-PC boundary

HYPOTHESIS-ID: m5-step1-retail-route-boundary

## Work unit

Run one driven retail-oracle route-boundary experiment before another port
pair. Watch the two guest PCs reported by the s2285/s2286 port failures:
`0x800547BC` and `0x80007904`. Keep the whole-RDRAM positive control first,
the eleven-Start schedule, `--vi-trace`, and title/hangar origin controls.
Phase-gate the watched-PC rows to the port's initial
`640 @ 0x00696100` route with `--pc-phase-log-width 0x00696100:640` and retain
the oracle's `exec-prev` attribution. This is an oracle-only experiment: do
not build, instrument, or change the port runtime.

## Competing hypotheses and discriminating measurement

- H-PortOnlyBadPath: the retail oracle passes whole-RDRAM, title, and hangar
  controls but records neither watched PC in the initial 640 phase. The port's
  `0x800547BC` crash path is then port-only at this recipe scope.
- H-RetailLegitimatePath: retail passes the controls and executes one or both
  PCs in the phase, with an `exec-prev` attribution, then reaches title and
  hangar. The boundary moves from audio/output nulls to port-side route/data/
  ABI behavior around a path retail actually uses.
- H-RetailRouteDifferent: retail passes the controls but executes the PCs only
  in another VI phase or with a different predecessor. The port and retail
  route identities differ, so another port pair is premature; investigate the
  route entry/overlay boundary rather than audio.
- H-OracleInvalid: the whole-RDRAM threshold or either title/hangar control is
  absent. The PC null or hit is uninterpretable and the experiment must be
  repaired before any port conclusion.

The discriminating measurement is one table containing: whole-RDRAM callback
threshold; title and hangar VI origins; every hit at `0x800547BC` and
`0x80007904` with live width/origin; and each hit's `exec-prev` caller. A
positive control is required before using any PC null. No image arm, audio
default, guard, or writer change follows this oracle result.

## Exact commands

1. Create `scratch/agent/run_s2287_m5_oracle_route_boundary.sh` with
   `apply_patch`. It should run from the repository root, create a capture
   directory whose final component does not begin with `.`, launch exactly
   one retail oracle, and use SIGKILL cleanup. Use:

   `tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 180 --watch-write 0x0:0x800000 --watch-pc 0x800547BC,0x80007904 --pc-phase-log-width 0x00696100:640 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`

2. Check syntax with `zsh -n` and run the script from the repository root.
3. Summarize only bounded grep/tail output: positive-control threshold,
   title/hangar VI rows, watched-PC rows, `exec-prev` summaries, and the
   oracle exit line. If the whole-RDRAM threshold or either target origin is
   missing, classify the result H-OracleInvalid and do not interpret PC
   coverage.
