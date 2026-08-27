# NEXT work unit (s2795) — close generated-symbol interval 0x80133000..0x80135000

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the bounded generated-symbol selector for guest interval
`0x80133000..0x80135000`. Apply only source-backed companion names, preserve
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
  python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
    --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
    --start-address 0x80133000 --end-address 0x80135000 --limit 32
  # Independently count placeholders in the same generated snapshot.
  python3 -c 'from pathlib import Path; import re; p=Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs"); xs=sorted(set(x for f in list(p.glob("funcs_*.c"))+[p/"funcs.h",p/"recomp_overlays.inl"] if f.exists() for x in re.findall(r"\\b(?:func|fake_func)_([0-9A-Fa-f]{8})\\b",f.read_text()) if 0x80133000<=int(x,16)<0x80135000)); print("\\n".join(("func_"+x for x in xs))); print("placeholder_unique="+str(len(xs)))'
  git diff --check
git status --short
```
