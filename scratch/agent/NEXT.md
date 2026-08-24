# NEXT work unit (s2289) — M5 Step 2 route requalification before default comparison

HYPOTHESIS-ID: m5-step2-route-requalification

## Work unit

Design and run one new route discriminator for the s2288 stub-first failure
before attempting the default-image arm again. The current binary already
defaults to the Factor 5 image and retains `ROGUESQ_AUDIO_UCODE=0`; do not
change that selection or add a guard, skip, writeback, C88 override, or route
workaround. The new arm must test a concrete route explanation and restore the
stub title/hangar gate, otherwise the default arm remains untested.

## Competing hypotheses and discriminating measurement

- H-RouteCause-A: the route failure follows the selected tested input/trace
  arm; restoring the specified missing route input produces the stub
  title/hangar gate without changing game logic.
- H-RouteCause-B: the route failure is independent of that input/trace arm and
  reproduces at the same guest PC; the current route remains invalid and the
  default arm must stay unlaunched.
- H-DefaultSafe: only if the stub gate is first restored, the default image
  reaches the same title/hangar route, and the full task/DMEM/DMA/service/
  slot/voice/PCM table remains complete.
- H-RouteInvalid: retail controls or the stub title/hangar gate is absent; no
  default-arm null or promotion is interpretable.

The discriminator is a same-build route matrix keyed by VI phase and route
ordinal, with the selected route input/trace arm and the s2288 stub control:
`audtask-dispatch → route phase → guest crash PC/terminal → title/hangar gate`.
The independent retail oracle must first pass the whole-RDRAM threshold and
title/hangar controls. If the stub gate is restored, launch the default arm
and collect the complete table: task ABI/source, DMEM/DMA, image exit, SP
completion, service, status/slot, voice/reap, PCM source/consumer, and
title/hangar phase. A dispatch or `Broke` return alone is only a branch
control, not a successful audio result.

## Exact commands

1. Ask ground truth for the chosen route discriminator and write the complete
   competing-hypothesis table above into this file before adding an instrument.

2. Build the single comparison executable only after the discriminator is
   specified:

   `cmake --build build --config Debug --target RogueSquadron64Recomp`

3. Create one self-contained driver with the same retail controls and the
   chosen route matrix. It must launch the stub control first, launch the
   default arm only after `vi_width=512 origin=0x006AB400`, keep both captures,
   watchdog each arm, SIGKILL every remaining game/oracle process, and exit
   nonzero when a required gate is absent. Run from `build/` with the ROM
   present; do not use SIGTERM.

4. Check and run exactly that driver:

   `zsh -n scratch/agent/<driver>.sh`

   `zsh scratch/agent/<driver>.sh`

5. Summarize only bounded driver summaries and marker counts. If either retail
   controls or the stub title/hangar gate is absent, classify H-RouteInvalid
   and do not interpret default-image nulls.

No image default promotion is complete until H-DefaultSafe is selected by the
full table and a later soak is queued with the same passive breadcrumbs.
