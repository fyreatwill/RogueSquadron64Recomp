# NEXT work unit — remaining texture-scratch rs_free clones

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of every generated
original `jal rs_free` in `loadBackdropAsset`,
`initCinematicSceneAssets`, and `buildPlayerCraftAssetTemplate`.
Remaining register-then-free scratch clones after the closed
text-texture class: the two `loadBackdropAsset` frees (`0x800AE468`
of `0x60($sp)`, `0x800AE4E0` of `0x10($s4)`), the one
`initCinematicSceneAssets` free (`0x800AE778` of `0x38($sp)`), and
the one `buildPlayerCraftAssetTemplate` free (`0x800639E4` of
`0x38($sp)`). Classify each pointer's writer and whether a free can
run on a non-allocator or already-freed value.
Do not repeat the closed text-texture rs_free class, format-message
rs_free, speech-file rs_free, speech/cache rs_free, destructor
skipped-NULL, destructor unchecked-free, `-0x6904` alias,
remaining-indexer, `-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`,
`+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`,
`+0x60`, MORT publication, mix-table, pan-input, or hangar-Y
audits. Do not change runtime code unless a concrete invalid
writer/value is identified; any mitigation needs an ORIGIN line
naming the writer and assessing legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: a remaining free can pass a pointer that is not the
  matching allocator store, or can free it after a sibling already
  released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of a
  matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Discriminator: the single complete original census of those
`jal rs_free` sites plus every original `sw` of each pointer. Select
Gap only with a concrete non-allocator or already-freed edge; select
Complete only when all remaining edges are covered; otherwise select
Unevaluable.

Exact checks before any build:

    grep -n -- 'loadBackdropAsset\|initCinematicSceneAssets\|buildPlayerCraftAssetTemplate' ../N64Recomp/RecompiledFuncs/funcs_*.c | head
    grep -n -- 'jal         0x80001C98' ../N64Recomp/RecompiledFuncs/funcs_28.c ../N64Recomp/RecompiledFuncs/funcs_14.c

No build or runtime run is expected for this static audit. If the census
is complete, write a new `docs/M3-S<session>-...md` evidence note and
update CURRENT-TRUTH, the ledger, status, outcome, and commit.
