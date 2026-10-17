# Next: bounded companion-symbol classification at `__osMotorinitialized = 0x80039120`.

The s5250 baseline arm self-skipped at host load1=5.20, so do not retry it
until a future loop supplies load1<2. M5 has no uncompleted de-stub step and
the recent M3 idiom classes are closed; continue the permitted sweep. The
previous `_Putfld` pointer was stale and was rechecked in s5266. The
`__osHwIntTable` candidate was confirmed as a data/fragment record in s5268;
the `__osShutdown` candidate was confirmed as a data/fragment record in s5269;
the `__OSGlobalIntMask` candidate was confirmed as a data/fragment record in
s5270; do not build or soak for them.

Before the next classification, competing hypotheses and discriminator:

- H1: `__osMotorinitialized` is already synchronized as a data symbol and needs no edit.
- H2: it is an unmaterialized callable placeholder whose companion name can be propagated.
- H3: it is a data/fragment record and must remain mechanical.

Discriminating measurement: run the bounded rename helper over only the next
candidate's span, then independently inspect its companion type, generated
body/header/overlay record, and references. A zero-edit data result selects
the data hypotheses; a callable generated placeholder with a safe companion
mapping selects the callable hypothesis.

Exact command:

`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x80039120 --end-address 0x80039130 --limit 1`

HYPOTHESIS-ID: generated-symbol-renaming-sweep
