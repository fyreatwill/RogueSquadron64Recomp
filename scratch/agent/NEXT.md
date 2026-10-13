# Resume bounded generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

One work unit: select one bounded audio-adjacent address range in the companion `rogue_squadron64` symbols and rename only functions whose identity is supported by an exact symbol/reference match. Record the mapping in the existing rename tool/source; do not regenerate or hand-edit generated output.

Competing hypotheses and discriminator:
- H1: the companion named symbol is an exact address match; the rename is safe.
- H2: m2c/decomp semantics provide a unique match but no exact named symbol; defer until corroborated.
- H3: neither source uniquely identifies the function; leave the placeholder unchanged.
The discriminating measurement is one static cross-reference table for every candidate in the chosen range: exact address, companion symbol, call/string references, and duplicate-name check. Any candidate with conflicting or absent evidence stays `func_*`.

Commands: inspect `tools/rename*`, enumerate the chosen range with `rg`, update the mapping using `apply_patch`, run the mapping's validator, and report the changed-count plus unresolved-count. No build is authorized unless the validator requires it.
