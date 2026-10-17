# Next: generated-symbol renaming sweep — `__osGetOneChannelData` candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

The M4 REVISIT phase-attributed the retail page writer and is complete. Resume
the bounded companion sweep at `__osGetOneChannelData = 0x80030A04`.
Determine whether it has a generated prologue/body, exact span to the next
companion entry, and an independent generated caller. Do not rename an ABI
symbol without all three gates.

Competing hypotheses and discriminator:

- H-generated-name-correct: body, exact span, and independent caller exist;
  preserve the semantic name or apply a justified rename.
- H-host-wrapper: only a runtime wrapper/declaration or zero-size record
  exists; preserve the ABI name.
- H-span-mismatch: a body exists but crosses a neighboring entry; leave it.
- H-unproven: evidence is incomplete; preserve the name and record why.

The discriminator is the bounded helper result plus generated-tree body/span
and caller counts. Run:

    rg -n '__osGetOneChannelData|func_80030A04|fake_func_80030A04' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
    python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x80030A04 --end-address 0x80030C00

No build or soak is needed for a naming-only or ABI-preservation result.
