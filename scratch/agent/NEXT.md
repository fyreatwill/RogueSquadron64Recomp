# NEXT work unit (s1609)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol renaming sweep with exactly one bounded
exact-name census over `0x800BF2F4..0x800BF358`. Do not build or run.
Record the address, size, generated definition, companion name/source,
caller or semantic evidence, and confidence before editing. Synchronize only
an exact independent name in `syms/rogue_squadron.syms.toml`; leave
address-encoded, fake, fragment, data-like, or ambiguous entries unchanged.

The TOML entry is `func_800BF2F4` with size `0x64`. The companion list and
generated overlay table are expected to identify `countTrailingZeros16` at
this address; the preceding `loadPlayerSlotHudPreset` body ends at
`0x800BF2F4`, and `applyResModeFromSettings` is the next live entry at
`0x800BF358`. Establish that boundary and verify the generated body/caller
before any rename.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized to `countTrailingZeros16`.
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
grep -n -C 5 -E '800BF2F4|800BF358|countTrailingZeros16|applyResModeFromSettings' ../rogue_squadron64/symbol_files/mission_overlay.txt
grep -n -C 4 -E '800BF2F4|800BF358|countTrailingZeros16' ../N64Recomp/RecompiledFuncs/funcs_33.c
grep -n -C 3 -E '800BF2F4|800BF358|countTrailingZeros16' syms/rogue_squadron.syms.toml
grep -n -C 3 -E 'countTrailingZeros16|applyResModeFromSettings' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl ../N64Recomp/RecompiledFuncs/funcs_33.c
rg -n -C 6 'jal         0x800BF2F4|countTrailingZeros16\(rdram' ../N64Recomp/RecompiledFuncs/funcs_*.c
```
