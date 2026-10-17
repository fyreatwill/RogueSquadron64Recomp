# Next: bounded companion-symbol classification at `__osHwIntTable = 0x800390E0`.

The s5250 baseline arm self-skipped at host load1=5.20, so do not retry it
until a future loop supplies load1<2. M5 has no uncompleted de-stub step and
the recent M3 idiom classes are closed; continue the permitted sweep. The
previous `_Putfld` pointer was stale and was rechecked in s5266.

Before the next classification, competing hypotheses and discriminator:

- H1: `__osHwIntTable` is already synchronized as a data symbol and needs no edit.
- H2: it is an unmaterialized callable placeholder whose companion name can be propagated.
- H3: it is a data/fragment record and must remain mechanical.

Discriminating measurement: run the bounded rename helper over exactly
`0x800390E0..0x80039100`, then independently inspect the companion type,
generated body/header/overlay record, and references. A zero-edit result with
data typing selects H1/H3; a callable generated placeholder with a safe
companion mapping selects H2.

Exact command:

`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x800390E0 --end-address 0x80039100 --limit 1`

HYPOTHESIS-ID: generated-symbol-renaming-sweep
