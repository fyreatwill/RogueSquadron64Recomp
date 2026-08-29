# Session 3067 — `fake_func_800B75C4`

## Discriminator

The competing hypotheses were:

- `H-ExactIdentity`: an independent source now names this record as a
  `playerYwingInit` preamble, permitting a regeneration-safe rename.
- `H-Fragment`: the record is a decoded fragment or boundary-only prefix and
  should retain its placeholder.
- `H-MappingDrift`: the companion and generated/project metadata disagree on
  address or extent.

The discriminator was the six-surface comparison: companion map and redefs,
generated body and callers, generated header/overlay registration, project
TOML/tooling, and current local duplicates.

## Surface comparison

| Surface | Finding | Result |
|---|---|---|
| Companion symbol map | `rogue_squadron64/symbol_files/mission_overlay.txt` retains `fake_func_800B75C4 = 0x800B75C4`; the following comment says `real function is playerYwingInit`, whose companion entry is `0x800B75D0` | Deliberate fake boundary before the real body; no semantic preamble name |
| Companion redefs | `build/redefs.txt` has `playerYwingInit` at `0x800B75D0` but no `800B75C4`, `fake_func_800B75C4`, or `playerYwingInitPreamble` entry | H-ExactIdentity has no independent companion name |
| Generated body | `RecompiledFuncs/funcs_31.c` decodes exactly `0x800B75C4..0x800B75CC` as `lui $at, 0x8005`, `lwc1 $f2, 0xC58($at)`, `mul.s $f0, $f0, $f2`; `playerYwingInit` begins at `0x800B75D0` | Three-instruction fragment with no prologue, return sequence, or standalone callable shape |
| Generated callers | Current generated tree has no call targeting `0x800B75C4`; callers in `funcs_31.c` target `playerYwingInit` at `0x800B75D0` | Callable entry is the adjacent Y-wing initializer, not the target record |
| Header / overlay registration | `funcs.h` declares the placeholder; `recomp_overlays.inl` registers it at offset `0x12494`, size `0xC`, followed by `playerYwingInit` at offset `0x124A0`, size `0x200` | Generated registration agrees with the exact boundary and extent |
| Project TOML / tooling / duplicates | `syms/rogue_squadron.syms.toml` matches the same placeholder, VRAM, and size; neither current rename tool maps it; no current duplicate conflicts exist. Historical backup files containing a temporary `playerYwingInitPreamble` are not live metadata and do not supply independent evidence | No mapping drift or supported semantic rename |

## Decision

`H-Fragment` selected. The companion's explicit fake-boundary comment and the
generated three-instruction extent establish that this is not a second
callable function, while `redefs.txt` supplies no semantic preamble identity.
The exact metadata agrees across the live generated tree and TOML, so
`H-MappingDrift` is rejected. Preserved `fake_func_800B75C4`; no generated,
TOML, tooling, build, or runtime change was justified.

The next unresolved sweep candidate is `fake_func_800B89F4`, immediately
before `playerVwingInit`.
