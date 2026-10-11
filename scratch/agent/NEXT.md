# NEXT: repeat the odd-physical-address PI-DMA producer audit on the hangar route
HYPOTHESIS-ID: odd-pi-dma-origin-audit

The s4622 trace covered both `osPiStartDma_recomp` and `osEPiStartDma_recomp`
into `do_dma`. The real-audio/LLE route reached title 1024 but not hangar; 16
bounded even control rows came from `osPiStartDma` with matching `do_dma` rows,
zero `osEPiStartDma` rows, and zero odd events. The independent retail oracle
passed its 10,000 whole-RDRAM control but stayed at 320-wide boot. No
hypothesis was selected.

Competing hypotheses:

- H-guest-dma: a legitimate guest PI-DMA request supplies the odd physical
  address; the caller and requested ROM record should be attributable and the
  retail oracle should show the corresponding transition.
- H-host-corruption: the guest request is even, but a host-side queue/ring or
  address transformation changes it before `do_rom_read`.
- H-stale-record: the odd request is a stale or corrupted DMA-ring record; the
  producer identity or ROM metadata will not match a live guest request.

Discriminator: one complete table of every odd-address assertion event,
including guest caller/return address, `osPiStartDma` physical address and
size, `do_dma` physical address and size, ring-slot identity, destination,
ROM metadata, and nearest retail/oracle phase. A qualified whole-RDRAM oracle
control and existing port VI/route control must be present. A matching
guest-to-`do_dma` pair selects H-guest-dma; an altered host pair selects
H-host-corruption; no live pair with a stale slot selects H-stale-record. No
alignment, skip, or mitigation is authorized.

Before building, arm ground truth first with the existing oracle whole-RDRAM
positive control and VI trace. Then use the canonical schedule
`ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`
with `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`, the real-audio/LLE controls, and
`ROGUESQ_LOG_S4622=1`. One capture must retain the complete s4622 table and
title/hangar controls. A guest-to-`do_dma` odd pair selects H-guest-dma; an
altered pair selects H-host-corruption; no live pair with a stale slot selects
H-stale-record. If hangar is missed again, report the result as unevaluable
and do not return to M4.
