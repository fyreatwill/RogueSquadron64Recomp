# Next: generated-symbol renaming sweep — `__osInsertTimer` candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run one bounded companion audit for `__osInsertTimer = 0x80034A48`; do not
build or soak.

Competing hypotheses and discriminator:

- H-generated-name-correct: generated body, exact span, and independent caller
  exist; preserve the semantic name or apply a justified rename.
- H-host-wrapper: only a runtime wrapper/declaration or zero-size record
  exists; preserve the ABI name.
- H-span-mismatch: a body exists but crosses a neighboring entry; leave it.
- H-unproven: evidence is incomplete; preserve the name and record why.

The discriminator is the bounded helper result plus generated-tree body/span
and caller counts. Run:

    rg -n '__osInsertTimer|func_80034A48|fake_func_80034A48' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
    python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x80034A48 --end-address 0x80034B4C
