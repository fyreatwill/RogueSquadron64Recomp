# NEXT: re-run the M4 accumulator boundary capture on the qualified hangar route
HYPOTHESIS-ID: m4-accumulator-boundary-qualified-hangar

RESUME: s4625 extended the canonical real-audio/LLE/ungated/solo/spin-yield
route for 120 seconds past hangar. It reached repeated VI 0x006AB400 at width
512, retained 16 even osPiStartDma/do_dma pairs, and emitted zero odd events.
The retail oracle whole-RDRAM control fired at 10,000 callbacks. The odd-PI
thread is parked as missing-trigger/alternate-route; M4 is now eligible.

Competing hypotheses:

- H-arithmetic: the accumulator diverges before the VGE/store boundary; M4
  rows should show a nonzero arithmetic mismatch before the store.
- H-vge-or-store: arithmetic matches but the VGE or store path diverges; rows
  should match through arithmetic and split at VGE/store attribution.
- H-source: the accumulator and store agree, but the source/input value is
  already divergent; paired rows should show source divergence before output.
- H-instrument-boundary: the stage-1 control fires but the hangar-phase join
  remains empty; the result is unevaluable and selects no runtime hypothesis.

Discriminator: one batched capture with the stage-1 positive control plus all
M4 arithmetic, VGE, store, and source rows phase-gated to the hangar origin
0x006AB400. A qualified hangar mismatch at arithmetic, VGE/store, or source
selects that arm; matching rows through all stages select no M4 fault; a
missing hangar row despite the control is an instrument-boundary null. Do not
interpret transient phase-3 rows.

Exact next commands:

1. `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Arm the retail oracle's whole-RDRAM positive control and VI trace before
   launching the port. Keep the M4 stage-1 control and all M4 join fields in
   one build/run. Use the canonical schedule with
   `ROGUESQ_AUTOPILOT_STOP_WIDTH=0`:
   `ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`
   with real audio, forced/ungated LLE, LLE-solo, and spin-yield controls.
3. Run from `build/` with the ROM present for 120 seconds, capture every arm
   to a path whose final component does not begin with `.`, and SIGKILL the
   game/process group. If hangar is missed, record the result as unevaluable.
