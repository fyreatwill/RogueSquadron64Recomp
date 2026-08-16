# NEXT work unit (s1576)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol renaming sweep with exactly one bounded
exact-name census over the next placeholder, `0x800B63C8..0x800B67A0`.
Do not build or run. Record its address, size, generated definition,
companion name/source, caller or semantic evidence, and confidence before
editing. Synchronize only an exact independent name in
`syms/rogue_squadron.syms.toml`; leave address-encoded, fake, or ambiguous
entries unchanged. This naming census does not reopen closed M5 audio
de-stubbing.

The TOML entry is `func_800B63C8` with size `0x3D8`. The companion mission
list maps `acquireLockOnTarget = 0x800B63C8`; the next named mission function
is `emitTexturedImpactEffect` at `0x800B67A0`. Synchronize only if the
complete comparison remains exact.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized to `acquireLockOnTarget`.
- H2: the mapping is partial, already-fake, or ambiguous, so the entry must
  remain unchanged.
- H3: no independent naming source exists and the region should be parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML live-body size and caller or semantic evidence
selects H1; an incomplete, already-fake, or conflicting match selects H2;
and no independent name selects H3. Each outcome selects one hypothesis.

Commands:

```
grep -n -C 5 -E '800B63C8|800B67A0|acquireLockOnTarget|emitTexturedImpactEffect' ../rogue_squadron64/symbol_files/mission_overlay.txt
grep -n -C 4 -E '800B63C8|800B67A0|acquireLockOnTarget|emitTexturedImpactEffect' ../N64Recomp/RecompiledFuncs/funcs_31.c
grep -n -C 3 -E '800B63C8|800B67A0|acquireLockOnTarget|emitTexturedImpactEffect' syms/rogue_squadron.syms.toml
```
