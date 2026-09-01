# NEXT work unit — audit the source fields feeding audio record selectors

HYPOTHESIS-ID: m3-audio-record-source-field-audit

Session 3589 completed the `0x4E/0x4F` selector/table-address census. The
relevant writers are `musyxKeyOnVoice` (source `+0x64` into destination
`+0x4E`) and `tickAudioChannel` (source `+0x58/+0x59` into `+0x4E/+0x4F`).
No concrete invalid value was found; do not repeat the consumer census or add
a guard.

Next work unit: audit every writer and initializer of source fields `+0x64`,
`+0x58`, and `+0x59` that feed the two audio-record selector writers. Follow
their call/record-base edges and classify the value ranges or sentinel
contracts. Land a guard only if a concrete invalid writer/value is identified.

Competing hypotheses and the discriminator:

- H-SourceFieldsBounded: `+0x64`, `+0x58`, and `+0x59` are bounded or use the
  documented `0xFF` fallback before publication.
- H-SourceFieldsUnsafe: a concrete source-field writer can publish an invalid
  selector value that reaches `0x4E/0x4F`.
- H-SourceFieldsMisread: the source offsets or record bases are misidentified.

Discriminator: enumerate every writer of the three source fields, every record
base/stride edge, and every bound/sentinel check before the selector stores.
Select unsafe only with a concrete writer and value; select bounded only when
all source writers and bases are covered; otherwise leave it unclassified. No
guard is authorized without an ORIGIN naming the legitimate writer and
assessing the value.

Exact checks:

    rg -n '0x64|0x58|0x59|0x4E|0x4F|musyxKeyOnVoice|tickAudioChannel' ../N64Recomp/RecompiledFuncs/funcs_20.c ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../N64Recomp/RecompiledFuncs/funcs_24.c
    rg -n '0x64|0x58|0x59' ../N64Recomp/RecompiledFuncs/funcs_*.c
