# NEXT work unit — audit the hangar 0x8000 Y/accumulator idiom

HYPOTHESIS-ID: m3-hangar-y-accumulator-idiom-audit

Session 3590 completed the `+0x64`/`+0x58`/`+0x59` source-field census. No
concrete invalid writer/value was found; do not repeat that census or add a
guard. See `docs/M3-S3590-AUDIO-SOURCE-FIELD-AUDIT.md`.

Next work unit: perform one complete grep-enumerate/classify audit of the
hangar `0x8000` Y/accumulator idiom named in CURRENT-TRUTH. Enumerate every
writer, consumer, record base/stride, and bound/sentinel check in the relevant
generated functions. Do not instrument or change runtime code unless the
audit identifies a concrete invalid writer/value; any mitigation would need
an ORIGIN line naming that writer and assessing legitimacy.

Competing hypotheses and the discriminator:

- H-HangarYBounded: every `0x8000` Y/accumulator writer is bounded and its
  consumers use a valid record/stride contract.
- H-HangarYUnsafe: a concrete writer publishes an invalid value or base that
  reaches the hangar failure.
- H-HangarYMisread: the suspected Y/accumulator field or record base is
  misidentified.

Discriminator: the complete writer/consumer/base table. Select unsafe only
with a concrete writer and value; select bounded only when all sites and bases
are covered; otherwise leave it unclassified.

Exact check:

    rg -n '0x8000|Y|accum|accumulator' ../N64Recomp/RecompiledFuncs/funcs_*.c
