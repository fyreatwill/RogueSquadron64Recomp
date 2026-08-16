# NEXT work unit (s1615)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run exactly one bounded census over `0x800BF784..0x800BF790`. Record the
address, size, generated definition, companion classification, and the
previous/next boundaries before editing. Do not rename an explicitly fake,
fragment, or data-like entry. Do not build or run.

Competing hypotheses and discriminator:

- H1: `fake_func_800BF784` is correctly classified as an explicit 0xC-byte
  fake fragment and must remain unchanged.
- H2: the companion classification or generated/TOML span conflicts with the
  fake label, so the entry needs a synchronized name or boundary correction.
- H3: the bytes are data-like or belong to `func_800BF790`, so the entry is a
  non-function boundary artifact and remains parked.

The complete comparison table is the discriminator: matching fake labels, an
exact 0xC generated/TOML span, and `func_800BF790` beginning at `0x800BF790`
select H1; a conflicting label or span selects H2; evidence that the entry is
not an independent function selects H3. Each outcome selects one hypothesis.

Commands:

```
rg -n -C 5 'fake_func_800BF784|800BF784|800BF790' ../rogue_squadron64/symbol_files/mission_overlay.txt
rg -n -C 6 '800BF784|800BF790' ../N64Recomp/RecompiledFuncs/funcs_33.c
rg -n '800BF784|800BF790' syms/rogue_squadron.syms.toml
rg -n -C 3 'fake_func_800BF784|func_800BF790' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Before starting the census, run `grep -n '^## Session ' PORTING-STATE.md |
tail -15`. If all 15 titles are sweep sessions, perform the mandatory
retail-entry-boundary or M4-accumulator revisit instead of this census.
