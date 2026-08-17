# NEXT work unit (s1760)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at leftover `fake_func_800DFB8C`
/ `0x800DFB8C` (size `0x4`). s1759 synchronized
`noopHandler_800DFB84`. Last-15 after this commit still
include s1744's revisit, so the mandatory REVISIT gate does not fire.

Competing hypotheses:

- H1: companion leftover `fake_func_800DFB8C`, generated body, TOML
  name/size, and overlay span already agree — confirm leftover only.
- H2: generated code still carries placeholder `func_800DFB8C` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800DFB8C` while generated/overlay already use the leftover name.
- H3: overlay collision, a second occupant, or size/boundary
  disagreement with the companion leftover listing (expected: the
  4-byte `addiu $sp, $sp, -0x18` fragment immediately before
  `applyCraftAnimAndDetailParams`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'fake_func_800DFB8C\|800DFB8C\|DFB8C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'fake_func_800DFB8C\|func_800DFB8C\|0x800DFB8C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_38.c
# toml + overlay inl
grep -n '800DFB8C\|fake_func_800DFB8C' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `fake_func_800DFB8C`,
  size `0x4`, previous `noopHandler_800DFB84` / `0x800DFB84`,
  next `applyCraftAnimAndDetailParams` / `0x800DFB90`,
  no leftover `func_800DFB8C` placeholder.
- H2: generated still `func_800DFB8C`, or TOML still `func_800DFB8C`
  while generated/overlay already use the leftover name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, a second occupant, or size != `0x4`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry recipe. Next cursor after this
address is `applyCraftAnimAndDetailParams` / `func_800DFB90`
(`0x800DFB90`, size `0x3C4`). Companion note: leftover splat;
`func_800DFB90` was deleted s432 as a duplicate-symbol collision with
`applyCraftAnimAndDetailParams`.
