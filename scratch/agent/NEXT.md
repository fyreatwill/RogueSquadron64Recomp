# NEXT work unit — producer entry-input contract

HYPOTHESIS-ID: m5-producer-entry-input-contract

Session 3415 selected `H-PortProducerZero`: the phase-qualified port pair
reached title and hangar, and `0x800078EC` wrote 384 zero-valued bytes per arm
into `0x1797B0:0x179A48`. Retail s3414 independently wrote nonzero data to the
same span. The next unit must locate the zeroing boundary at producer entry.

Competing hypotheses and the single discriminating measurement:

- H-PortEntryInputZero: port enters `0x800078EC` with the source pointer or
  input bytes already zero; entry arguments/pointed payload differ from retail.
- H-PortEntryTransformZero: port entry arguments and pointed input match the
  retail contract, but the producer's internal loop emits zero bytes.
- H-PortEntryRouteMismatch: port reaches the same numeric PC through a
  different caller/route or with a different control tuple, so the apparent
  producer comparison is not like-for-like.

The discriminator is one phase-qualified retail oracle entry-argument table
and one fresh-build port silent/image pair with the same batched entry witness.
Require whole-RDRAM, title 1024, hangar 512, producer, ABI/DMA, image-stage,
and PCM controls. An identical nonzero entry tuple with zero port stores selects
H-PortEntryTransformZero; a zero/different input selects H-PortEntryInputZero;
a different caller/control tuple selects H-PortEntryRouteMismatch. If the
retail phase bucket or any positive control is absent, classify unevaluable.

Exact ground-truth command shape:

`tools/oracle/build/rs64_oracle --core <debug-core> --rom <retail-rom> --secs 120 --watch-write 0x0:0x800000 --watch-pc 0x800078EC --pc-phase-log-width 0x006AB400:512 --pc-field-dump 0x800078EC`

Then add only the matching phase-scoped port entry witness, build once, and
run both arms from `build/` using the s3411 route controls. Do not change
waits, slots, dispatch, clear behavior, or PCM writeback.
