# NEXT work unit (s2792) — close generated-symbol interval 0x8012D000..0x8012F000

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the bounded generated-symbol selector for guest interval
`0x8012D000..0x8012F000`. Apply only source-backed companion names, preserve
ambiguous/data entries, then independently scan the generated tree for
placeholder definitions/references in the same interval. This is one rename
interval; do not repair the unrelated duplicate generated definition or add
runtime probes.

## Competing hypotheses and discriminator

- H-no-placeholders: the interval has no generated placeholder definitions or
  references, so the selector should make zero changes.
- H-synchronized: the interval has companion entries, but all generated
  symbols are already human-mapped; the selector should preserve them and
  still make zero changes.
- H-source-backed-renames: the interval contains unambiguous companion names
  for generated placeholders; the selector should change those references.
- H-ambiguous-data: candidate entries are data, fake, or ambiguous; they must
  be reported and preserved rather than renamed.

The discriminator is the complete interval table: selector changes by file,
independent placeholder-definition/reference counts, and preserved
ambiguous/data candidates. A nonzero source-backed change selects
H-source-backed-renames; zero placeholders selects H-no-placeholders; existing
human mappings with zero changes selects H-synchronized; preserved candidates
selects H-ambiguous-data for those entries.

## Exact commands

```sh
rg -n "8012D000|8012F000|selector|rename" docs tools scratch/agent
# Run the existing bounded selector command identified by that search.
git diff --check
git status --short
```
