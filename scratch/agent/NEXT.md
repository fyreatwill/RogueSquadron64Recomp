# Next: generated-symbol renaming sweep — `__osClearPage` candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Bounded work unit: audit only companion `__osClearPage = 0x8002F2C8`, the next
entry after classified `__osPfsDeclarePage`. Determine whether it has a
generated prologue/body, exact span, and independent caller. Do not rename an
ABI symbol without all three gates.

Competing hypotheses and discriminator:

- H-generated-name-correct: a generated prologue/body is at `0x8002F2C8`, the
  overlay span ends at the next entry, and an independent generated caller
  exists; apply the semantic rename.
- H-host-wrapper: only a runtime wrapper/call declaration exists, or the
  overlay record has `rom_size = 0`; preserve the `_recomp` ABI name.
- H-span-mismatch: a generated body exists but its address/span crosses a
  neighboring entry; leave it unchanged.
- H-unproven: no usable semantic companion evidence or live caller; leave it
  unchanged and record why.

Discriminating measurement: compare the companion address with a generated
prologue, inspect the overlay record and next-entry boundary, and count direct
generated callers in one bounded inspection. Each outcome selects rename,
preserve ABI naming, leave unchanged, or advance without a build/soak.

Commands:

    rg -n '__osClearPage|func_8002F2C8|fake_func_8002F2C8' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
    python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x8002F2C8 --end-address 0x8002F350

If all generated-name gates pass, apply the explicit mapping and record a new
audit. Otherwise preserve the wrapper ABI and record the classification. No
build or soak is needed for a naming-only or host-wrapper result.
