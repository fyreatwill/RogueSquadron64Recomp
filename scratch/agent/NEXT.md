# NEXT work unit — audit the MusyX voice-table envelope companion `+0x5C`/`+0x64`

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of the MusyX voice-table
envelope companion fields `+0x5C` and `+0x64` across
`RecompiledFuncs/funcs_23.c` (`advanceVolumeFadeEnvelope`) and
`RecompiledFuncs/funcs_24.c` (attack/release/fade/init). Session 3598 showed
voice-table `+0x68` is a float copy of `+0x5C` and `+0x6C` is the phase byte
consumed by `advanceVolumeFadeEnvelope`, not the command-list volume
halfword. Enumerate every word/halfword/byte writer and reader, effective
base/layout, index derivation, reset/free ordering, and consumer bound.
Do not repeat the closed `+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table, pan-input, or hangar-Y
audits. Do not change runtime code unless a concrete invalid writer/value
is identified; any mitigation needs an ORIGIN line naming the writer and
assessing legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: the field family contains a concrete invalid writer/value or
  unchecked writer-to-consumer edge.
- H-NextClassComplete: every writer, consumer, base, lifetime, and bound is
  structurally covered and only runtime legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed layouts prevent a complete
  object-level classification.

Discriminator: the single complete `+0x5C`/`+0x64` census spanning both
files, including the already-identified `+0x68`/`+0x6C` envelope edges in
`advanceVolumeFadeEnvelope`. Select Gap only with a concrete invalid edge;
select Complete only when all edges are covered; otherwise select
Unevaluable.

Exact checks before any build:

    rg -n 'MEM_[BHW].*(0X5C|0X64)' ../N64Recomp/RecompiledFuncs/funcs_23.c ../N64Recomp/RecompiledFuncs/funcs_24.c
    rg -n 'void advanceVolumeFadeEnvelope|void musyxTriggerVoiceAttack|void musyxStartVoiceRelease|void beginVoiceFadeRelease' ../N64Recomp/RecompiledFuncs/funcs_23.c ../N64Recomp/RecompiledFuncs/funcs_24.c

No build or runtime run is expected for this static audit. If the census is
complete, write a new `docs/M3-S<session>-...md` evidence note and update
CURRENT-TRUTH, the ledger, status, outcome, and commit.
