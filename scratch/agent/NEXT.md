# NEXT: resume the odd-physical-address PI-DMA producer audit on the hangar route
HYPOTHESIS-ID: odd-pi-dma-origin-audit

RESUME: s4622's batched trace is already landed and qualified only through
title VI 1024. Do not rerun a title-only recipe or interpret its zero odd
events as global evidence. The prior retry stopped before this audit could be
completed; this iteration only checkpointed that boundary.

Competing hypotheses remain:

- H-guest-dma: a legitimate guest PI-DMA request supplies the odd physical
  address; caller and ROM metadata should match a live guest request.
- H-host-corruption: the guest request is even, but a host queue/ring or
  address transformation changes it before `do_rom_read`.
- H-stale-record: the odd request is stale/corrupt DMA-ring state with no
  matching live guest request or ROM record.

Discriminator: one complete table for every odd event, joining guest caller
and return PC, `osPiStartDma`/`osEPiStartDma` arguments, converged `do_dma`
arguments, ring slot, destination, ROM metadata, and phase. A matching live
guest-to-`do_dma` pair selects H-guest-dma; an altered pair selects
H-host-corruption; an odd event with no live guest pair and stale slot selects
H-stale-record. A whole-RDRAM retail watch and port VI/route controls must
fire in the same capture. No alignment, skip, or mitigation is authorized.

Exact next commands:

1. `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Arm the retail oracle's whole-RDRAM positive control and VI trace before
   launching the port. Preserve the s4622 `s4622-dma` trace and use the
   canonical schedule:
   `ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`
   with `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`, real audio, forced/ungated LLE,
   LLE-solo, and spin-yield controls.
3. Run from `build/` with the ROM present, capture every arm to a path whose
   final component does not begin with `.`, and SIGKILL the game/process
   group. If hangar is missed, record the result as unevaluable and do not
   return to M4.
