# NEXT work unit (s1611)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run exactly one bounded exact-name census over
`0x800BF3A4..0x800BF408`. Record the address, size, generated definition,
companion name/source, caller or semantic evidence, and confidence before
editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, fragment,
data-like, or ambiguous entries unchanged. Do not build or run.

The TOML entry is `func_800BF3A4` with size `0x64`. The companion list and
generated overlay table are expected to identify `restoreGameSettingsAfterDemo`
at this address; `applyResModeFromSettings` ends at `0x800BF3A4`, and
`loadAndStartDemo` is the next live entry at `0x800BF408`. Establish that
boundary and verify the generated body and callers/semantics before any
rename.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized to `restoreGameSettingsAfterDemo`.
- H2: the mapping is partial or conflicting, or the generated/TOML span does
  not match, so the entry must remain unchanged.
- H3: the region is a fragment/data-like or otherwise non-function region
  lacking an independent naming basis, so it should remain parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML live-body size, exact previous and next
boundaries, and caller or semantic evidence selects H1; a conflicting or
incomplete boundary/name selects H2; and no independent name or a
non-function region selects H3. Each outcome selects one hypothesis.

Commands:

```
rg -n '800BF3A4|800BF408|restoreGameSettingsAfterDemo|loadAndStartDemo' ../rogue_squadron64/symbol_files/mission_overlay.txt
rg -n -C 5 '800BF3A4|800BF408|restoreGameSettingsAfterDemo|loadAndStartDemo' ../N64Recomp/RecompiledFuncs/funcs_33.c
rg -n '800BF3A4|800BF408|restoreGameSettingsAfterDemo|loadAndStartDemo' syms/rogue_squadron.syms.toml
rg -n -C 3 'applyResModeFromSettings|restoreGameSettingsAfterDemo|loadAndStartDemo' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
rg -n -C 6 'jal[[:space:]]+0x800BF3A4|restoreGameSettingsAfterDemo\(rdram' ../N64Recomp/RecompiledFuncs/funcs_*.c
```
