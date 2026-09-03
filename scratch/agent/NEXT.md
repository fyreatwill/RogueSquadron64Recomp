# NEXT work unit — `-0x6904` voice-table pointer alias

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of every generated
original access to `lui 0x8015; lw/sw -0x6904` (the malloc alias of the
`0x88` voice-table pointer stored beside `-0x6908`). Classify
`allocateSongChannelArray` (store + init walk), `shutdownAudioEngine`
(free at `0x80091E48`), and `waitForMusyXAudioTaskDone` (free at
`0x80091F98`), including whether the pointer is a live allocator result,
a stale alias after the other free, or an untrusted load.
Do not repeat the closed remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table, pan-input, or
hangar-Y audits. Do not change runtime code unless a concrete invalid
writer/value is identified; any mitigation needs an ORIGIN line naming
the writer and assessing legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: a remaining `-0x6904` user can free or walk a pointer
  that is not the live `allocateSongChannelArray` result, or can use it
  after the sibling free.
- H-NextClassComplete: every remaining alias user is the allocator store,
  the count-bounded init walk, or a destructor of that same pointer, and
  only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed lifetimes prevent a complete
  object-level classification of the pointer source.

Discriminator: the single complete original `-0x6904` census across
`funcs_23.c` and `funcs_24.c`, plus every generated JAL of
`waitForMusyXAudioTaskDone`. Select Gap only with a concrete stale-free
or untrusted-pointer edge; select Complete only when all remaining edges
are covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- '-0x6904\|-0X6904' ../N64Recomp/RecompiledFuncs/funcs_23.c ../N64Recomp/RecompiledFuncs/funcs_24.c

No build or runtime run is expected for this static audit. If the census
is complete, write a new `docs/M3-S<session>-...md` evidence note and
update CURRENT-TRUTH, the ledger, status, outcome, and commit.
