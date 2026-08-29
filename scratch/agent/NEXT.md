# NEXT work unit — bounded callable-placeholder census in `0x800A0000..0x800B0000`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Session 3159 renamed the exact companion-qualified callable records
`static_5_800AF6AC` → `handleCraftSelectInput` and
`static_4_800E9B10` → `initObjectAnimAndDetail`. Continue the sweep under one
stable slug; do not rename ambiguous fragments or data-gap records.

## Single work unit

Enumerate every remaining generated placeholder in the address band
`0x800A0000..0x800B0000`, join each address against the companion symbol
files, and select at most one bounded batch of exact semantic callable names.
If the band has no such match, close this sweep lead and return to the
retail-grounded M5 boundary rather than inventing names.

Competing hypotheses and discriminator:

- `H-SemanticMatches`: at least one remaining placeholder has one exact,
  non-fake companion callable name and a generated body/caller. Rename only
  those rows through the helper.
- `H-AmbiguousFragments`: candidates are companion fake/data-gap records or
  split fragments. Preserve their placeholders and record the classification.
- `H-NoReachablePlaceholder`: remaining candidates have no generated body or
  caller and are not actionable callable symbols.

The discriminating measurement is one address table containing placeholder,
companion name/type, generated body span, and caller/reference count. A
unique semantic callable row selects `H-SemanticMatches`; only fake/data-gap
or split rows selects `H-AmbiguousFragments`; no body/caller rows selects
`H-NoReachablePlaceholder`.

Exact starting commands:

```sh
python3 - <<'PY'
from pathlib import Path
import re
root = Path('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs')
text = '\n'.join(p.read_text() for p in sorted(root.glob('funcs_*.c')) + [root/'funcs.h', root/'recomp_overlays.inl'] if p.exists())
for addr in sorted(set(re.findall(r'\b(?:func|fake_func|static_[0-9]+)_([0-9A-Fa-f]{8})\b', text))):
    n = int(addr, 16)
    if 0x800A0000 <= n < 0x800B0000:
        print(addr)
PY
rg -n '^(?!D_|fake_func_|func_)[A-Za-z_][A-Za-z0-9_]*\s*=\s*0x800A' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Expected outcomes: exact callable matches are renamed in one bounded batch;
ambiguous/data-gap rows remain untouched; an empty callable set closes this
lead. No runtime probe or build is authorized for this naming discriminator.
