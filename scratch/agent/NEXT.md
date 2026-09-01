# NEXT work unit — audit the MusyX voice `+0x28..+0x2C` field family

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of the MusyX voice
`+0x28..+0x2C` field family in `RecompiledFuncs/funcs_24.c`. Enumerate every
word/halfword writer and reader, effective base/layout, index derivation,
reset/free ordering, and consumer bound. Do not repeat the closed `+0x60`,
`+0x30..+0x40`,
MORT publication, mix-table, pan-input, or hangar-Y audits. Do not change
runtime code unless a concrete invalid writer/value is identified; any
mitigation needs an ORIGIN line naming the writer and assessing legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: the field family contains a concrete invalid writer/value or
  unchecked writer-to-consumer edge.
- H-NextClassComplete: every writer, consumer, base, lifetime, and bound is
  structurally covered and only runtime legitimacy remains.
- H-NextClassUnevaluable: word/halfword aliases or mixed layouts prevent a
  complete object-level classification.

Discriminator: the single complete `+0x28..+0x2C` census. Select Gap only
with a concrete invalid edge; select Complete only when all edges are covered;
otherwise select Unevaluable.

Exact checks before any build:

    rg -n 'MEM_[BHW].*(0X28|0X2A|0X2C)' ../N64Recomp/RecompiledFuncs/funcs_24.c
    rg -n 'RECOMP_FUNC|musyx(RenderVoiceSamples|KeyOnVoice|MixActiveVoices|InitVoiceFromSample|StartVoiceRelease)' ../N64Recomp/RecompiledFuncs/funcs_24.c

No build or runtime run is expected for this static audit. If the census is
complete, write a new `scratch/agent/M3-S<session>-...md` evidence note and
update CURRENT-TRUTH, the ledger, status, outcome, and commit.
