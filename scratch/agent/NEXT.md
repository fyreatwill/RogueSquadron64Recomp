# NEXT: test whether the odd PI-DMA requires post-hangar stimulus
HYPOTHESIS-ID: odd-pi-dma-post-hangar-trigger

RESUME: s4624 reached repeated hangar VI 0x006AB400 on the canonical schedule
and emitted 16 even osPiStartDma/do_dma pairs but no odd event. The hangar
route is qualified, but the recurring odd request was not triggered.

Competing hypotheses remain:

- H-post-hangar-trigger: continued autopilot input after the first hangar
  phase causes a legitimate odd guest request; it should appear as a paired
  guest-entry/do_dma row.
- H-missing-trigger: the odd request needs a different input/save/route event;
  the extended canonical route will still show no odd row.
- H-host-or-stale: an odd row appears without a matching live guest entry, or
  with altered arguments at do_dma.

Discriminator: one complete table for every odd event, joined to guest entry,
converged do_dma arguments, destination, ROM metadata, and VI phase. An odd
paired row after continued input selects H-post-hangar-trigger; no odd row
through the extended route selects H-missing-trigger; an unpaired or altered
odd row selects H-host-or-stale. The retail whole-RDRAM control and port VI
controls must fire in the same capture. No alignment, skip, or mitigation is
authorized.

Exact next commands:

1. `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Arm the retail oracle's whole-RDRAM positive control and VI trace before
   launching the port. Preserve the s4622 `s4622-dma` trace and use the
   canonical schedule with `ROGUESQ_AUTOPILOT_STOP_WIDTH=0`:
   `ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`
   with real audio, forced/ungated LLE, LLE-solo, and spin-yield controls.
3. Run from `build/` with the ROM present for 120 seconds, capture every arm
   to a path whose final component does not begin with `.`, and SIGKILL the
   game/process group. If hangar is missed, record the result as unevaluable
   and do not return to M4.
