# NEXT work unit (s1610)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run exactly one bounded exact-name census over
`0x800BF358..0x800BF3A4`. Record the address, size, generated definition,
companion name/source, caller or semantic evidence, and confidence before
editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, fragment,
data-like, or ambiguous entries unchanged. Do not build or run.

The TOML entry is `func_800BF358` with size `0x4C`. The companion list and
generated overlay table are expected to identify `applyResModeFromSettings` at
this address; the preceding `countTrailingZeros16` body ends at
`0x800BF358`, and `restoreGameSettingsAfterDemo` is the next live entry at
`0x800BF3A4`. Establish that boundary and verify the generated body and
callers/semantics before any rename.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized to `applyResModeFromSettings`.
- H2: the mapping is partial or conflicting, or the generated/TOML span does
  not match, so the entry must remain unchanged.
- H3: the region is a fragment/data-like or otherwise non-function region
  lacking an independent naming basis, so it should remain parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML live-body size, exact next boundary, and caller
or semantic evidence selects H1; a conflicting or incomplete boundary/name
selects H2; and no independent name or a non-function region selects H3.
Each outcome selects one hypothesis.

Commands:

```
grep -n -C 5 -E '800BF358|800BF3A4|applyResModeFromSettings|restoreGameSettingsAfterDemo' ../rogue_squadron64/symbol_files/mission_overlay.txt
grep -n -C 5 -E '800BF358|800BF3A4|applyResModeFromSettings' ../N64Recomp/RecompiledFuncs/funcs_33.c
grep -n -C 3 -E '800BF358|800BF3A4|applyResModeFromSettings' syms/rogue_squadron.syms.toml
grep -n -C 3 -E 'countTrailingZeros16|applyResModeFromSettings|restoreGameSettingsAfterDemo' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl ../N64Recomp/RecompiledFuncs/funcs_33.c
rg -n -C 6 'jal         0x800BF358|applyResModeFromSettings\(rdram' ../N64Recomp/RecompiledFuncs/funcs_*.c
```
