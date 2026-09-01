# NEXT work unit — requalify the pre-title MusyX route before dispatcher analysis

HYPOTHESIS-ID: m5-pretitle-musyx-route-requalification

Do one bounded route requalification at `musyxSynthFrame+3828`, last guest PC
`0x80001B08`, which preempted the dispatcher table in session 3555. Before
building, enumerate that generated function around the PC, its callers, the
immediate state read, and candidate guest writers. Do not change heap, audio,
PCM, image-task, output, or texture records.

Competing hypotheses and discriminator:

- H-PreTitleAudioRoute: the real-audio route is unstable before the selected
  dispatcher boundary; the new MusyX boundary will show a repeatable state or
  route failure.
- H-DispatcherInput: a route-valid run reaches `0x80007904` with malformed
  slot data and a named writer before the failing read.
- H-DispatcherRoute: a route-valid run reaches the dispatcher with valid slot
  data but a lifecycle/phase sequence mismatch.
- H-DispatcherOverlay: a route-valid run shows expected slot data but a wrong
  overlay/function body or function-map selection.

The discriminator is one same-build, phase-scoped table at the MusyX boundary
covering entry, immediate read, writer/value breadcrumb, and return/exit,
retaining the existing autopilot, VI, and slot-dispatch controls. A stable bad
state with a named writer selects input; valid state plus route divergence
selects route; absent new rows with live controls selects native crash artifact.
Do not add a guard or rewrite a value. Run all fields in one build/run and use
SIGKILL cleanup from `build/`.

Required pre-build census:

    rg -n "musyxSynthFrame|0x80001B08|80001B08|0x80090|voice.*state" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py src docs
    grep -n '^## Session ' PORTING-STATE.md | tail -15

Positive controls must visibly fire in the same run: `[autopilot]`, VI width
transitions, existing `[slot-dispatch]` rows, and zero/explicit count for the
new MusyX table. Run from `build/` on the canonical real-audio/LLE-solo/
spin-yield/autopilot route; phase-gate analysis by VI, never elapsed time.
