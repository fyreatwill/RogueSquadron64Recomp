# Next work unit: locate the M5 image preimage producer

HYPOTHESIS-ID: m5-image-preimage-producer

Competing hypotheses and discriminator written before the next build:

- H-source-zero: the port's source RDRAM bytes are already zero before the
  image DMA.
- H-DMA-zero: the port source bytes are nonzero but the DMA into `DMEM 0xCC0`
  is zero or mis-sized.
- H-route-misjoin: the source-DMA witness cannot be joined to a qualified
  stage-0 row, so the apparent preimage null is a task-generation mismatch.
- H-control-invalid: if retail whole-RDRAM/title/hangar controls or either
  image target phase fails, the corresponding null is unevaluable.

The single discriminating measurement is one same-build, retail-grounded,
phase-gated source-DMA matrix for declared and legacy image arms. Retail
ground truth qualified the physical input/working span
`0x178C80..0x178F18` (664 writes; hangar snapshot nonzero=24); the paired port
capture qualified both target VIs and found stage-0 DMEM `0xCC0` zero in both
arms. Instrument the source RDRAM bytes, DMA source/length/destination, and
stage-0 join in one table, retaining task generation and PCM controls. A
qualified nonzero source followed by zero DMEM selects H-DMA-zero; zero source
selects H-source-zero; missing generation/task joins select H-route-misjoin.
Retail whole-RDRAM/title/hangar and both port image target VIs are mandatory
positive controls; a missing phase makes that arm unevaluable.

ORIGIN: the candidate values are legitimate image source bytes and DMA
payloads; the host staging writer already proved that `0x800` versus `0xF80`
is not the sufficient contract divergence. No skip, force-clear, or guest
behavior change is authorized.

Exact work: first run a retail oracle watch on `0x178C80..0x178F18` with the
whole-RDRAM positive control and both target phase gates. Then add one
regeneration-safe source-DMA witness covering the full input range and its
`DMEM 0xCC0` destination, rebuild once, and run declared/legacy together with
the existing stage/task/PCM controls. Expected outcomes: nonzero source plus
zero DMEM selects H-DMA-zero; zero source selects H-source-zero; absent joins
select H-route-misjoin. Any missing title/hangar gate invalidates that arm.
