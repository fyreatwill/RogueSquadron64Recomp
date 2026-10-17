# Next: generated-symbol renaming sweep — next companion candidate after `__osProbeTLB`
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Select the next named companion entry after `__osProbeTLB = 0x800351A0` from
`rogue_squadron64/symbol_files/libultra.txt`, namely
`__osViSwapContext = 0x80035550`, then run one bounded companion audit with
`tools/rename_generated_symbols.py`; do not build or soak. Record the exact
address and end boundary in the next NEXT.md.

Competing hypotheses and discriminator:

- H-generated-name-correct: generated body, exact span, and independent caller
  exist; preserve the semantic name or apply a justified rename.
- H-host-wrapper: only a runtime wrapper/declaration or zero-size record
  exists; preserve the ABI name.
- H-span-mismatch: a body exists but crosses a neighboring entry; leave it.
- H-unproven: evidence is incomplete; preserve the name and record why.

The discriminator is the bounded helper result plus generated-tree body/span
and caller counts. Run:

    rg -n '__osViSwapContext|func_80035550|fake_func_80035550' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
    python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x80035550 --end-address 0x80035A00
