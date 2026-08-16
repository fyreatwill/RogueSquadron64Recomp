# NEXT work unit (s1614)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Run exactly one bounded census over `0x800BF498..0x800BF4A0`. Record the
address, size, generated definition, companion classification, and the
previous/next boundaries before editing. Do not rename an explicitly fake,
fragment, or data-like entry. Do not build or run.

The TOML entry is `fake_func_800BF498` with size `0x8`. The companion mission
symbol list also marks `0x800BF498` as `fake_func_800BF498`; the generated body
is an `lw`/`sw` frame fragment, and `attached3DSoundEmitterNpcHandler` begins
at `0x800BF4A0`.

Competing hypotheses and discriminator:

- H1: the entry is a correctly classified fake two-instruction fragment and
  must remain unchanged.
- H2: the companion classification or generated span conflicts with the
  fake label, so the TOML entry needs a different synchronized name.
- H3: the bytes are data-like or belong to the following handler, so the
  entry should remain parked as a non-function boundary artifact.

The complete comparison table is the discriminator: matching fake labels,
an exact 0x8 generated/TOML span, and the next handler at `0x800BF4A0` select
H1; a conflicting label or span selects H2; and evidence that the entry is
not an independent function selects H3. Each outcome selects one hypothesis.

Commands:

```
rg -n -C 5 'fake_func_800BF498|800BF498|800BF4A0|attached3DSoundEmitterNpcHandler' ../rogue_squadron64/symbol_files/mission_overlay.txt
rg -n -C 6 '800BF498|800BF4A0|attached3DSoundEmitterNpcHandler' ../N64Recomp/RecompiledFuncs/funcs_33.c
rg -n '800BF498|800BF4A0|attached3DSoundEmitterNpcHandler' syms/rogue_squadron.syms.toml
rg -n -C 3 'fake_func_800BF498|attached3DSoundEmitterNpcHandler' ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
```
