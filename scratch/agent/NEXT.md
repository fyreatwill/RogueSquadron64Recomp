# Next: generated-symbol renaming sweep — `__osPfsReleasePages` candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

The mandatory REVISIT is complete. Resume the bounded companion sweep: audit
only `__osPfsReleasePages = 0x800303D0`, immediately after the classified
`osPfsDeleteFile`. Its next companion boundary is `0x80030618`. Determine
whether it has a generated prologue/body, exact span, and independent
caller. Do not rename an ABI symbol without all three gates.

Competing hypotheses and discriminator:

- H-generated-name-correct: generated body at the candidate address, exact
  span to the following entry, and an independent generated caller; apply the
  rename.
- H-host-wrapper: only a runtime wrapper/declaration or zero-size overlay
  record; preserve the ABI name.
- H-span-mismatch: a body exists but crosses a neighboring entry; leave it.
- H-unproven: no usable semantic body/caller evidence; preserve the name.

Run:

    rg -n '__osPfsReleasePages|func_800303D0|fake_func_800303D0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
    python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x800303D0 --end-address 0x80030618

No build or soak is needed for a naming-only or ABI-preservation result.
