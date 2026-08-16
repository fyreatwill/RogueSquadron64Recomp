# NEXT work unit (s1579)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol renaming sweep with exactly one bounded
exact-name census over the next placeholder, `0x800B7590..0x800B75C4`.
Do not build or run. Record its address, size, generated definition,
companion name/source, caller or semantic evidence, and confidence before
editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or ambiguous
entries unchanged. This naming census does not reopen M5 audio de-stubbing.

The TOML entry is `func_800B7590` with size `0x34`. The companion mission
list maps `findLockOnTarget = 0x800B7590`; the next entry is the already-fake
`fake_func_800B75C4` at `0x800B75C4`. Synchronize only if the complete
comparison remains exact.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized to `findLockOnTarget`.
- H2: the mapping is partial, already-fake, or ambiguous, so the entry must
  remain unchanged.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML live-body size and caller or semantic evidence
selects H1; an incomplete, already-fake, or conflicting match selects H2;
and no independent name selects H3. Each outcome selects one hypothesis.

Commands:

```
grep -n -C 5 -E '800B7590|800B75C4|findLockOnTarget|fake_func_800B75C4' ../rogue_squadron64/symbol_files/mission_overlay.txt
grep -n -C 4 -E '800B7590|800B75C4|findLockOnTarget|fake_func_800B75C4' ../N64Recomp/RecompiledFuncs/funcs_31.c
grep -n -C 3 -E '800B7590|800B75C4|findLockOnTarget|fake_func_800B75C4' syms/rogue_squadron.syms.toml
```
