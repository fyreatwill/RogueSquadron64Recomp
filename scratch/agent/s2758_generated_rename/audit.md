# Session 2758 generated-symbol interval census

## Scope

`0x800EF000..0x800F1000`, end exclusive, using the active generated tree in
`../N64Recomp/RecompiledFuncs` and all companion `symbol_files/*.txt` entries.

## Competing hypotheses and discriminator

- H1: every placeholder in the interval has a defensible companion/source name.
- H2: some entries are fake/address-only or ambiguous and must remain.
- H3: an apparent match is a duplicate/alias whose references make renaming
  unsafe.

The discriminator was the complete interval census plus the generated-tree
placeholder search: each address must classify as selected, already
synchronized, preserved fake/ambiguous/address-only, or unsafe alias.

## Evidence

The bounded rename tool reported zero renamed references in zero files and
returned its intentional no-selection error under `--require-rename`.
Companion candidates were already synchronized for the semantic entries in
the interval, including the music, cue, NPC, actor, and animation helpers.
The two companion entries `fake_func_800EFD74` and `fake_func_800EFDDC` were
classified `ambiguous-or-fake` and were preserved.

An independent `rg` scan over every generated C file, header, and overlay
table found zero stale `func_`/`fake_func_` placeholders in the interval.
`build_redefs.py` completed and regenerated 9,801 companion redef lines;
`git diff --check` passed.

## Decision

H2 is selected for the two explicit fake entries. H1 is false as a blanket
claim because those entries have no defensible semantic name. H3 had no
selected alias to test. No generated symbols were changed. The next bounded
interval is `0x800F3000..0x800F5000`.
