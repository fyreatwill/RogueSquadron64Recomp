# NEXT work unit — compare port writer-loop internal state

HYPOTHESIS-ID: m5-writer-loop-internal-state

Session 3420 selected H-RetailEntryZero: retail's 664 target writes enter with
the same a0/a1/a2 tuple as the port, and the store callback's live phase is
width 1024/origin 0x006AB800. Entry arguments are not the missing edge.

Competing hypotheses and the single discriminating measurement:

- H-PortWriterStateDiffers: the port's internal writer registers or pointed
  state differ before the first target store, identifying the next divergence.
- H-PortWriterStateMatches: the writer-loop state matches retail, moving the
  gap to the subsequent publication boundary.
- H-PortWriterRouteDiffers: the port's target stores use a different caller or
  state object despite matching entry arguments.

The discriminator is one fresh-build port pair with a complete bounded
writer-loop tuple at 0x800078EC for the target span, including ra, a0/a1/a2,
t0/t1, s0/s1, source pointers/fields, first v0, and target predicate. Keep
whole-route, title 1024, hangar 512, audio ABI/DMA, image-stage, and PCM
controls. A missing phase or control is unevaluable.

Implement the witness through the regeneration-safe fixup path, build once,
and run silent and Factor 5 image arms concurrently. Do not change waits,
slots, dispatch, clear behavior, or PCM writeback.
