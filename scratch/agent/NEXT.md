# NEXT work unit (s1583)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol renaming sweep with exactly one bounded
exact-name census over the next placeholder, `0x800B88C8..0x800B89F4`.
Do not build or run. Record its address, size, generated definition,
companion name/source, caller or semantic evidence, and confidence before
editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or ambiguous
entries unchanged. This naming census does not reopen M5 audio de-stubbing.

The TOML entry is `func_800B88C8` with size `0x12C`. The companion mission
list maps `emitTexturedEffectCue = 0x800B88C8`; the generated definition
already uses `emitTexturedEffectCue`. The next function is
`fake_func_800B89F4` at `0x800B89F4`.
Synchronize only if the complete comparison remains exact.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized to `emitTexturedEffectCue`.
- H2: the mapping is partial, conflicting, or the generated/TOML span does
  not match, so the entry must remain unchanged.
- H3: the region is a fragment/data-like or otherwise lacks an independent
  naming basis, so it should remain parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML live-body size and caller or semantic evidence
selects H1; a conflicting or incomplete boundary/name selects H2; and no
independent name or a non-function region selects H3. Each outcome selects
one hypothesis.

Commands:

```
grep -n -C 5 -E '800B88C8|800B89F4|emitTexturedEffectCue' ../rogue_squadron64/symbol_files/mission_overlay.txt
grep -n -C 4 -E '800B88C8|800B89F4|emitTexturedEffectCue' ../N64Recomp/RecompiledFuncs/funcs_31.c
grep -n -C 3 -E '800B88C8|800B89F4|emitTexturedEffectCue' syms/rogue_squadron.syms.toml
```
