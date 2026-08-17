# NEXT work unit (s1757)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `npcGroundTransportUpdate`
/ `0x800DE80C` (size `0x136C`). s1756 synchronized
`npcGroundTransportPlayFriendlyFireWarn`. Last-15 after this commit still
include s1744's revisit, so the mandatory REVISIT gate does not fire.

Competing hypotheses:

- H1: companion `npcGroundTransportUpdate`, generated body, TOML
  name/size, and overlay span already agree — confirm only.
- H2: generated code still carries placeholder `func_800DE80C` (or a
  stale alias) and needs a TOML + fixup rename.
- H3: overlay collision, leftover `fake_func_*`, or size/boundary
  disagreement with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'npcGroundTransportUpdate\|800DE80C\|DE80C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'npcGroundTransportUpdate\|func_800DE80C\|0x800DE80C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_38.c
# toml + overlay inl
grep -n '800DE80C\|npcGroundTransportUpdate' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `npcGroundTransportUpdate`,
  size `0x136C`, previous `npcGroundTransportPlayFriendlyFireWarn` /
  `0x800DE4EC`, next `func_800DFB78` / `resetCraftSubsystemGlobal` /
  `0x800DFB78`, no leftover placeholder.
- H2: generated still `func_800DE80C`, or TOML still `func_800DE80C`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, leftover splat, or size != `0x136C`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry recipe. Next cursor after this
address is whatever the census names as the following mission function.
The companion voiceId `0x217` site is at `0x800DF988` inside this
function (`jal 0x80066EE4`) — confirm it on the live body, do not
re-attribute it to `0x800DE4EC`.
