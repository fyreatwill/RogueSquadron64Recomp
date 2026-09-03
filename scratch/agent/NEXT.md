# NEXT work unit — remaining -0x6908 table-base users (non-a0)

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of every generated
function that loads `lui 0x8015; lw -0x6908` (the `0x88` voice-table
base) but does NOT form `D_801496F8 + a0*0x88` from incoming `a0`.
Classify `musyxMixActiveVoices`, `musyxRenderVoiceSamples`,
`musyxKeyOnVoice`, `musyxSynthFrame`, `shutdownAudioEngine`, and
`allocateSongChannelArray`, including every offset added to that base
and whether the offset is a live-count walk, a malloc size, or an
untrusted index.
Do not repeat the closed remaining-indexer, release/fade, `+0x5C`/`+0x64`,
`+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`,
MORT publication, mix-table, pan-input, or hangar-Y audits. Do not change
runtime code unless a concrete invalid writer/value is identified; any
mitigation needs an ORIGIN line naming the writer and assessing
legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: a remaining `-0x6908` user can index the `0x88` table
  with an untrusted or sentinel value (not the live-count walk and not
  the malloc size).
- H-NextClassComplete: every remaining base user is a count-bounded
  walk, a table allocator, or a non-index load, and only runtime
  allocator legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed layouts prevent a complete
  object-level classification of the offset source.

Discriminator: the single complete remaining `-0x6908` non-a0 census
across `funcs_23.c` and `funcs_24.c`. Select Gap only with a concrete
out-of-range or sentinel-as-index edge; select Complete only when all
remaining edges are covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- '-0x6908\|-0X6908' ../N64Recomp/RecompiledFuncs/funcs_23.c ../N64Recomp/RecompiledFuncs/funcs_24.c

No build or runtime run is expected for this static audit. If the census
is complete, write a new `docs/M3-S<session>-...md` evidence note and
update CURRENT-TRUTH, the ledger, status, outcome, and commit.
