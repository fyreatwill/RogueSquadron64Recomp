# NEXT work unit (s1884)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F2A00` (`0x800F2A00`,
size `0x24`). After s1883 the last-15 titles still include
s1872's hangar/512 revisit, so this is not a mandatory REVISIT.

s1872 parked hangar/512 as UNEVALUABLE (no port arm published
origin `0x006ab400` / `0x006ab800`). Do not reopen that window
without a `[phase] vi_width=512 origin=0x006AB400` log.

Companion `mission_overlay.txt` (line 1028) and generated
`funcs.h` / `recomp_overlays.inl` already name
`getObjectNpcTypeId` (10 callers, convenience accessor returning
`findActiveNpcInSlotChain(obj+0x130, NULL)`); TOML still leftover
`func_800F2A00` (`syms/rogue_squadron.syms.toml:1983`). Overlay
INL offset `0x0004D8D0`, `rom_size 0x24` — contiguous with
`getObjectMeshTransformOrLocal`'s `0x0004D858 + 0x78 = 0x0004D8D0`.

Competing hypotheses:

- H1 already-named: companion, generated headers/body/INL, and
  TOML already agree on one human name — confirm only.
- H2 TOML leftover: generated side already uses
  `getObjectNpcTypeId`; TOML still `func_800F2A00`
  — synchronize TOML (and any remaining generated leftover).
- H3 invent: no trustworthy human name; leave `func_*`.

Exact commands:

```
# Confirm generated funcs_41.c body at 0x800F2A00 matches the
# companion's findActiveNpcInSlotChain-wrapper description; grep
# generated *.c/*.h/*.inl for leftover "func_800F2A00\b" (expect
# zero hits outside the TOML). Then rename the TOML entry.
grep -n "800F2A00" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_41.c
grep -rn 'func_800F2A00\b' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.inl
```

Expected splits:

- H1: every source already agrees; session title
  `confirmed the leftover … symbol`.
- H2 (expected, per neighbor peek above): synchronize TOML to
  `getObjectNpcTypeId`; title `synchronized the … symbol`.
- H3: leave leftover; document why.

Do not start another hangar/512 LLE walk.
