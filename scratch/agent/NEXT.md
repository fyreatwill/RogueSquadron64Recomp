# NEXT work unit — remaining 0x88-stride voice-table indexers

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of every generated
function that forms `D_801496F8 + idx*0x88` (`lui 0x8015; lw -0x6908`
then `(idx<<4)+idx<<3`) OTHER than the two consumers closed in session
3600 (`musyxStartVoiceRelease`, `beginVoiceFadeRelease`). Classify every
direct caller of `isAudioSlotActive`, `stopVoiceMarkRetrigger`,
`musyxInitVoiceFromSample`, `musyxStoreVoiceAdsrParams`, `musyxStopVoice`,
`musyxSetVoicePitchBend`, `deactivateVoice`, `getVoiceUserField`, and
any remaining mix/attack indexer, including whether `a0` is masked,
count-bounded, or taken from packed-handle `+0x67`.
Do not repeat the closed release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, or hangar-Y audits. Do not change
runtime code unless a concrete invalid writer/value is identified; any
mitigation needs an ORIGIN line naming the writer and assessing
legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: a live remaining indexer can pass `0xFF` from the `-1`
  packed-handle low byte, or another out-of-range index, into the `0x88`
  voice table.
- H-NextClassComplete: every remaining caller argument is a slot below
  the live count or is structurally gated before the JAL, and only
  runtime allocator legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed layouts prevent a complete
  object-level classification of the index source.

Discriminator: the single complete remaining-indexer/caller census
across `funcs_22.c` through `funcs_24.c`. Select Gap only with a
concrete out-of-range or sentinel-as-index edge; select Complete only
when all remaining edges are covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n 'isAudioSlotActive\|stopVoiceMarkRetrigger\|musyxInitVoiceFromSample\|musyxStoreVoiceAdsrParams\|musyxStopVoice\|musyxSetVoicePitchBend\|deactivateVoice\|getVoiceUserField\|musyxTriggerVoiceAttack' ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../N64Recomp/RecompiledFuncs/funcs_24.c

No build or runtime run is expected for this static audit. If the census
is complete, write a new `docs/M3-S<session>-...md` evidence note and
update CURRENT-TRUTH, the ledger, status, outcome, and commit.
