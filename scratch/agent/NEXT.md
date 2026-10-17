# Next: generated-symbol renaming sweep — `__osPfsSelectBank` candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

The mandatory REVISIT is complete. Resume the bounded companion sweep: audit
only `__osPfsSelectBank = 0x8003007C`, immediately after the classified
`__osPfsRWInode`. Its next companion boundary is `0x800303D0`. Determine
whether it has a generated prologue/body, exact span, and independent
caller. Do not rename an ABI symbol without all three gates.

Competing hypotheses and discriminator:

- H-generated-name-correct: generated body at the next companion address, exact
  span to the following entry, and an independent generated caller; apply the
  rename.
- H-host-wrapper: only a runtime wrapper/declaration or zero-size overlay
  record; preserve the ABI name.
- H-span-mismatch: a body exists but crosses a neighboring entry; leave it.
- H-unproven: no usable semantic body/caller evidence; preserve the name.

Run:

    rg -n '__osPfsSelectBank|func_8003007C|fake_func_8003007C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
    python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x8003007C --end-address 0x800303D0

No build or soak is needed for a naming-only or ABI-preservation result.
