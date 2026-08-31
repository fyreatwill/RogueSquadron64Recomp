# NEXT work unit — join retail target writes to writer-loop state

HYPOTHESIS-ID: m5-retail-target-writer-state

Session 3421 selected H-PortWriterStateDiffers only against the retail
ordinary-loop control: the port target rows have s0=0x12/s1=0x5622, while
retail's ordinary 512 loop has s0=a0/s1=0x18. The exact target-row state is
not yet joined on the retail side.

Competing hypotheses and the single discriminating measurement:

- H-RetailTargetStateDiffers: retail target stores at this PC have a distinct
  internal state, so the port's unusual s0/s1 may be legitimate route state.
- H-RetailTargetStateMatches: retail target stores have the ordinary
  s0=a0/s1=0x18 shape, identifying a port caller/register-state divergence.
- H-RetailTargetOtherWriter: retail target-span writes are not made by
  0x800078EC, so the proposed PC join is the wrong boundary.

The discriminator is one fresh-build port pair with a complete bounded
writer-loop tuple at 0x800078EC for the target span, including ra, a0/a1/a2,
t0/t1, s0/s1, source pointers/fields, first v0, and target predicate. Keep
whole-route, title 1024, hangar 512, audio ABI/DMA, image-stage, and PCM
controls. A missing phase or control is unevaluable. The next discriminator
must join the exact target-span writes to the watched execution state.

Do not change waits, slots, dispatch, clear behavior, or PCM writeback.
