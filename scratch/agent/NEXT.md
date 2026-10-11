# NEXT: audit the complete odd-physical-address PI-DMA producer class
HYPOTHESIS-ID: odd-pi-dma-origin-audit

The s4621 repeat reached the same port phase and emitted 2,112 phase-3 target
rows, but the known `do_rom_read` assertion for an odd physical ROM address
stopped the port before any hangar row. The retail oracle passed its
whole-RDRAM control at 10,000 callbacks but reached title only. Four M4
attempts have not produced the discriminator, so this thread is pivoted.

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
positive control and VI trace. Then instrument all producer arms in one
build/run. The next work unit is one bounded source audit plus one batched
capture; do not return to M4 until this table names the writer.
