# NEXT work unit (s1758)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `resetCraftSubsystemGlobal`
/ `0x800DFB78` (size `0xC`). s1757 confirmed
`npcGroundTransportUpdate`. Last-15 after this commit still
include s1744's revisit, so the mandatory REVISIT gate does not fire.

Competing hypotheses:

- H1: companion `resetCraftSubsystemGlobal`, generated body, TOML
  name/size, and overlay span already agree — confirm only.
- H2: generated code still carries placeholder `func_800DFB78` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800DFB78` while generated/overlay already use the human name.
- H3: overlay collision, leftover `fake_func_*`, or size/boundary
  disagreement with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'resetCraftSubsystemGlobal\|800DFB78\|DFB78' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'resetCraftSubsystemGlobal\|func_800DFB78\|0x800DFB78' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_38.c
# toml + overlay inl
grep -n '800DFB78\|resetCraftSubsystemGlobal' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `resetCraftSubsystemGlobal`,
  size `0xC`, previous `npcGroundTransportUpdate` / `0x800DE80C`,
  next `noopHandler_800DFB84` / `func_800DFB84` / `0x800DFB84`,
  no leftover placeholder.
- H2: generated still `func_800DFB78`, or TOML still `func_800DFB78`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, leftover splat, or size != `0xC`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry recipe. Next cursor after this
address is whatever the census names as the following mission function
(`noopHandler_800DFB84` / `fake_func_800DFB8C` / `applyCraftAnimAndDetailParams`).
Companion comment: "clears a craft-subsystem global counter" — the live
body is `sw $zero, -0x3F60($v0)` with `$v0 = 0x80110000`, i.e. store 0
to `0x8010C0A0` (the same global case 4 of `npcGroundTransportUpdate`
compares before playing voiceId `0x217`).
