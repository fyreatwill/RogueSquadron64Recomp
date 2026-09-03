# NEXT work unit — skipped-NULL destructor-free class

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of every generated
original `lw; beq $zero; jal rs_free` in `shutdownAudioEngine`,
`waitForMusyXAudioTaskDone`, `shutdownMusyXEngine`, and `musyxNoopStub`.
Remaining skipped-NULL destructor pointers after the closed unchecked
class: `-0x6898` (also stores zero before free), `-0x6890`, and wrapper
`-0x50EC`. Classify each pointer's writer and whether a free can run
on a non-allocator or already-freed value.
Do not repeat the closed destructor unchecked-free class, `-0x6904`
alias, remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table, pan-input, or
hangar-Y audits. Do not change runtime code unless a concrete invalid
writer/value is identified; any mitigation needs an ORIGIN line naming
the writer and assessing legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: a remaining skipped free can pass a pointer that is
  not the matching allocator store, or can free it after a sibling
  destructor already released it without a NULL.
- H-NextClassComplete: every remaining skipped free is a destructor of
  a matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Discriminator: the single complete original census of those
`lw; beq $zero; jal rs_free` sites plus every original `sw` of each
pointer. Select Gap only with a concrete non-allocator or already-freed
edge; select Complete only when all remaining edges are covered;
otherwise select Unevaluable.

Exact checks before any build:

    grep -n -- '-0x6898\|-0x6890\|-0x50EC' ../N64Recomp/RecompiledFuncs/funcs_23.c ../N64Recomp/RecompiledFuncs/funcs_24.c

No build or runtime run is expected for this static audit. If the census
is complete, write a new `docs/M3-S<session>-...md` evidence note and
update CURRENT-TRUTH, the ledger, status, outcome, and commit.
