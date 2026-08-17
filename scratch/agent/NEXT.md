# NEXT work unit (s1759)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `noopHandler_800DFB84`
/ `0x800DFB84` (size `0x8`). s1758 synchronized
`resetCraftSubsystemGlobal`. Last-15 after this commit still
include s1744's revisit, so the mandatory REVISIT gate does not fire.

Competing hypotheses:

- H1: companion `noopHandler_800DFB84`, generated body, TOML
  name/size, and overlay span already agree — confirm only.
- H2: generated code still carries placeholder `func_800DFB84` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800DFB84` while generated/overlay already use the human name.
- H3: overlay collision, leftover `fake_func_*`, or size/boundary
  disagreement with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'noopHandler_800DFB84\|800DFB84\|DFB84' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'noopHandler_800DFB84\|func_800DFB84\|0x800DFB84' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_38.c
# toml + overlay inl
grep -n '800DFB84\|noopHandler_800DFB84' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `noopHandler_800DFB84`,
  size `0x8`, previous `resetCraftSubsystemGlobal` / `0x800DFB78`,
  next `fake_func_800DFB8C` / `0x800DFB8C`,
  no leftover placeholder.
- H2: generated still `func_800DFB84`, or TOML still `func_800DFB84`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, leftover splat, or size != `0x8`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry recipe. Next cursor after this
address is whatever the census names as the following mission function
(`fake_func_800DFB8C` / `applyCraftAnimAndDetailParams`).
Companion comment: "pure jr-ra stub".
