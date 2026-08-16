# NEXT work unit (s1616)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run exactly one bounded census over `0x800BF790..0x800BFDC4`. Record the
address, size, generated definition/body, companion references, and the
previous/next boundaries before editing. Synchronize a name only if an
independent companion name and the generated/TOML/overlay span agree. Do not
build or run.

Competing hypotheses and discriminator:

- H1: `func_800BF790` has an independently supported semantic name in the
  companion project, and its live generated body plus exact span support a
  synchronized rename.
- H2: the companion project has no independent semantic name for this entry,
  so the address-encoded placeholder remains the least-assumptive label.
- H3: the generated/TOML/overlay boundaries conflict or the bytes are
  data-like/non-independent, so the entry remains parked pending correction.

The complete comparison table is the discriminator: an independent companion
name plus a live generated body, matching `0x634` TOML/overlay span, and the
exact preceding `fake_func_800BF784` and following `func_800BFDC4` boundaries
select H1; no independent companion name with otherwise coherent boundaries
selects H2; any span conflict or non-function evidence selects H3. Each
outcome selects one hypothesis.

Commands:

```
rg -n -C 8 '800BF790|func_800BF790' ../rogue_squadron64
rg -n -C 12 '800BF790|800BFDC4' ../N64Recomp/RecompiledFuncs/funcs_33.c
rg -n -C 3 '800BF790|800BFDC4' syms/rogue_squadron.syms.toml
rg -n -C 3 'func_800BF790|func_800BFDC4' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Before starting the census, run `grep -n '^## Session ' PORTING-STATE.md |
tail -15`. If all 15 titles are sweep sessions, perform the mandatory
retail-entry-boundary or M4-accumulator revisit instead of this census.
