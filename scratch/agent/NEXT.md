# NEXT work unit (s1772)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol census at `buildDebrisTransformStack`
/ `func_800E1F5C` (`0x800E1F5C`, size `0x4A0`). s1771 synchronized
`tickTrainCarStateMachine`; neighbor peek already shows TOML still
`func_800E1F5C` while generated/overlay use the human name. Last-15
titles after s1771 still include s1760's revisit, so the all-sweep
10→10→10→15→REVISIT gate does not fire.

Competing hypotheses:

- H1: companion, generated body, TOML name/size, and overlay span already
  agree on `buildDebrisTransformStack` — confirm only.
- H2: generated code still carries placeholder `func_800E1F5C` (or a
  stale alias) and needs a TOML + fixup rename, or TOML is still
  `func_800E1F5C` while generated/overlay already use the human name.
  Neighbor peek from s1771 already saw this TOML/overlay split — confirm
  it on the live body before renaming.
- H3: overlay collision, a leftover splat, or size/boundary disagreement
  with the companion listing.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (read-only census; no game run):

```
# companion
grep -n 'buildDebrisTransformStack\|func_800E1F5C\|800E1F5C\|E1F5C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
# generated
grep -n 'buildDebrisTransformStack\|func_800E1F5C\|0x800E1F5C' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_39.c
# toml + overlay inl
grep -n '800E1F5C\|buildDebrisTransformStack\|func_800E1F5C' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: all four sources already say `buildDebrisTransformStack`,
  size `0x4A0`, previous `tickTrainCarStateMachine` /
  `0x800E1E1C`, next `slerpFrameTowardTargetAxis` /
  `0x800E23FC`, no leftover `func_800E1F5C` placeholder.
- H2: generated still `func_800E1F5C`, or TOML still `func_800E1F5C`
  while generated/overlay already use the human name — rename in TOML
  and the fixup path.
- H3: menu/cinematic occupant, a leftover splat at this address, or
  size != `0x4A0`.
- H4: a required source is absent.

Do not reopen the attract-1024 six-entry or jump-table recipes. Next
cursor after this address is `slerpFrameTowardTargetAxis`
(`0x800E23FC`).
