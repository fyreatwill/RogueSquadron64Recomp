# Next: bounded generated-symbol sweep at `_Genld = 0x80036620`.

The s5250 baseline arm self-skipped at host load1=5.20, so do not retry it
until a future loop supplies load1<2. M5 has no uncompleted de-stub step and
the recent M3 idiom classes are closed; continue the permitted sweep.

Before the next classification, competing hypotheses and discriminator:

- H1: `_Genld` is already synchronized and needs no edit.
- H2: `_Genld` is a placeholder whose companion name can be propagated.
- H3: the address is a data/fragment record and must remain mechanical.

Discriminating measurement: run the bounded rename helper over exactly
`0x80036620..0x80036B90`, then independently inspect the companion symbol,
generated body/header/overlay record, and callers. A zero-edit result plus a
full matching body selects H1; a safe companion-to-placeholder rename selects
H2; no callable body or fragment evidence selects H3.

Exact command:

`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x80036620 --end-address 0x80036B90 --limit 1`

HYPOTHESIS-ID: generated-symbol-renaming-sweep
