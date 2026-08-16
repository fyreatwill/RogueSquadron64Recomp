# NEXT work unit (s1594)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol renaming sweep with exactly one bounded
exact-name census over `0x800BBF6C..0x800BC290`. Do not build or run.
Record the address, size, generated definition, companion name/source,
caller or semantic evidence, and confidence before editing. Synchronize only
an exact independent name in `syms/rogue_squadron.syms.toml`; leave
address-encoded, fake, fragment, data-like, or ambiguous entries unchanged.

The TOML entry is `func_800BBF6C` with size `0x324`. The companion mission list
maps `computeTieInterceptorTransform = 0x800BBF6C`; the adjacent known
function is `triggerTieInterceptorEffect` at `0x800BC290`. The generated
overlay table and `funcs_32.c` should establish the live-body boundary and
caller or semantic evidence.

Competing hypotheses and discriminator:

- H1: the function has an exact independent companion mapping and can be
  synchronized to `computeTieInterceptorTransform`.
- H2: the mapping is partial or conflicting, or the generated/TOML span does
  not match, so the entry must remain unchanged.
- H3: the region is a fragment/data-like or otherwise non-function region
  lacking an independent naming basis, so it should remain parked.

The complete comparison table is the discriminator: an exact companion name
with matching generated/TOML live-body size and caller or semantic evidence
selects H1; a conflicting or incomplete boundary/name selects H2; and no
independent name or a non-function region selects H3. Each outcome selects
one hypothesis.

Commands:

```
grep -n -C 5 -E '800BBF6C|800BC290|computeTieInterceptorTransform' ../rogue_squadron64/symbol_files/mission_overlay.txt
grep -n -C 4 -E '800BBF6C|800BC290|computeTieInterceptorTransform' ../N64Recomp/RecompiledFuncs/funcs_31.c ../N64Recomp/RecompiledFuncs/funcs_32.c
grep -n -C 3 -E '800BBF6C|800BC290|computeTieInterceptorTransform' syms/rogue_squadron.syms.toml
grep -n -C 3 'computeTieInterceptorTransform' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl ../N64Recomp/RecompiledFuncs/funcs_31.c ../N64Recomp/RecompiledFuncs/funcs_32.c
```
