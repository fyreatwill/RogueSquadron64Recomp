# Next: generated-symbol renaming sweep — motor-start candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Bounded work unit: audit only companion `osMotorStart = 0x8002D570`, the next
libultra entry after the classified motor-stop entry. Determine whether it has a
generated prologue/body or is another runtime wrapper. Do not rename a `_recomp`
ABI symbol without a generated body and exact span.

Competing hypotheses and discriminator:

- H-generated-name-correct: a generated prologue/body is at `0x8002D570`, the
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

    rg -n 'osMotorStart|func_8002D570|fake_func_8002D570' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
    python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x8002D570 --end-address 0x8002D88C

If all generated-name gates pass, apply the explicit mapping and record a new
audit. Otherwise preserve the wrapper ABI and record the classification. No
build or soak is needed for a naming-only or host-wrapper result.

The prior REVISIT is closed for this cycle: the independent retail cxd4 run
sampled 3,048,760 mid-task graphics states, including 289 hangar tasks, with
zero `0x8000` VACC lanes; completion-state and mid-task controls both fired.
