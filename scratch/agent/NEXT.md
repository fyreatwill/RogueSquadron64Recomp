# Next: generated-symbol renaming sweep — `osSpTaskLoad` candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Audit `osSpTaskLoad = 0x80033E3C` as one bounded companion unit. Determine
whether it has a generated prologue/body, exact span to the next companion
entry, and an independent generated caller. Do not rename an ABI symbol
without all three gates.

Competing hypotheses and discriminator:

- H-generated-name-correct: body, exact span, and independent caller exist;
  preserve the semantic name or apply a justified rename.
- H-host-wrapper: only a runtime wrapper/declaration or zero-size record
  exists; preserve the ABI name.
- H-span-mismatch: a body exists but crosses a neighboring entry; leave it.
- H-unproven: evidence is incomplete; preserve the name and record why.

The discriminator is the bounded helper result plus generated-tree body/span
and caller counts. Run:

    rg -n 'osSpTaskLoad|func_80033E3C|fake_func_80033E3C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
    python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x80033E3C --end-address 0x80034010

No build or soak is needed for a naming-only or ABI-preservation result.
