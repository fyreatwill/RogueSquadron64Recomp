# NEXT work unit — bounded producer loop-entry witness

HYPOTHESIS-ID: m5-producer-entry-input-contract

Session 3416 left the producer entry contract unevaluable: image reached title
and hangar with zero-valued target-span writes, while silent crashed before the
target phase. The entry witness captured only the title clear. Retail s3414
independently wrote nonzero data to the same span. The next unit must capture
the actual loop-entry arguments for hangar writes.

Competing hypotheses and the single discriminating measurement:

- H-PortEntryInputZero: port's `a0/a1/a2` or pointed source is already zero or
  differs from retail at the first target-span loop entry.
- H-PortEntryTransformZero: port's entry tuple matches retail and is nonzero,
  but the loop's computed `v0`/store value becomes zero.
- H-PortEntryRouteMismatch: port's target write reaches the numeric PC through
  a different caller/control tuple, so the comparison is not like-for-like.

The discriminator is one phase-qualified retail store-field table and one
fresh-build port silent/image pair with the same batched loop-entry witness.
Require whole-RDRAM, title 1024, hangar 512, producer, ABI/DMA, image-stage,
and PCM controls. An identical nonzero entry tuple with zero port stores selects
H-PortEntryTransformZero; a zero/different input selects H-PortEntryInputZero;
a different caller/control tuple selects H-PortEntryRouteMismatch. If the
retail phase bucket or any positive control is absent, classify unevaluable.

Instrument through the regeneration-safe fixup path at the first
`0x800078EC` loop iteration, passing `ctx->r4`, `ctx->r5`, `ctx->r6`, and
computed `ctx->r2` to a phase-scoped host witness. Exact ground-truth command:

`tools/oracle/build/rs64_oracle --core <debug-core> --rom <retail-rom> --secs 120 --watch-write 0x0:0x800000 --watch-pc 0x800078EC --pc-phase-log-width 0x006AB400:512 --pc-field-dump 0x800078EC`

Then add only the matching phase-scoped port loop-entry witness, build once,
and run both arms from `build/` using the s3411 route controls. Do not change
waits, slots, dispatch, clear behavior, or PCM writeback.
