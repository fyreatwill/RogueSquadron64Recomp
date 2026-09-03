# NEXT work unit — audit the MusyX voice `+0x66..+0x74` publication family

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of the MusyX
`+0x66..+0x74` publication family in `RecompiledFuncs/funcs_24.c`. Session
3597 showed `musyxRenderVoiceSamples` copies voice-table volume halfwords
into command-list `s0+0x66..+0x74`, and `musyxKeyOnVoice` divides
`+0x6A/+0x72` and `+0x6C/+0x74` by `+0x60` to produce dest slope words.
Enumerate every word/halfword/byte writer and reader, effective base/layout,
index derivation, reset/free ordering, and consumer bound. Do not repeat the
closed `+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, or hangar-Y audits. Do not change runtime
code unless a concrete invalid writer/value is identified; any mitigation
needs an ORIGIN line naming the writer and assessing legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: the field family contains a concrete invalid writer/value or
  unchecked writer-to-consumer edge.
- H-NextClassComplete: every writer, consumer, base, lifetime, and bound is
  structurally covered and only runtime legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed layouts prevent a complete
  object-level classification.

Discriminator: the single complete `+0x66..+0x74` census. Select Gap only
with a concrete invalid edge; select Complete only when all edges are covered;
otherwise select Unevaluable.

Exact checks before any build:

    python3 -c "import pathlib,re; t=pathlib.Path('../N64Recomp/RecompiledFuncs/funcs_24.c').read_text(); print(sum(1 for _ in re.finditer(r'MEM_[BHW].*(0[xX]6[6-9A-Fa-f]|0[xX]7[0-4])', t)))"
    rg -n 'MEM_[BHW].*(0X66|0X68|0X6A|0X6C|0X6E|0X70|0X72|0X74)' ../N64Recomp/RecompiledFuncs/funcs_24.c

No build or runtime run is expected for this static audit. If the census is
complete, write a new `docs/M3-S<session>-...md` evidence note and update
CURRENT-TRUTH, the ledger, status, outcome, and commit.
