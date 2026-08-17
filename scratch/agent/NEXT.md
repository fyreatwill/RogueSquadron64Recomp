# NEXT work unit (s1797)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover `func_800E8948` / `applyCraftAnimDetailParamsB`
census. Last-15 ledger titles after s1796 include the s1792 revisit
(`selected H3 unwatched submitGfx callers`), so the 15-title all-sweep
REVISIT gate does not fire.

Census leftover `func_800E8948` / companion `applyCraftAnimDetailParamsB`
(`0x800E8948`, size `0xEC`). Neighbor peek already: TOML still carries
`func_800E8948`; generated headers/body, overlay INL, and
`mission_overlay.txt` already use the human name (likely H2 TOML-only).
Next leftover after it is `fake_func_800E8A34` (`0x800E8A34`, size `0xC`).

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `applyCraftAnimDetailParamsB` (confirm only;
  no rename).
- H2: one source still carries a stale `func_800E8948` placeholder.
  Fix the stale source (neighbor peek: TOML).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `playAttachmentCueNoTexture` ends at `0x800E8948`; next
  occupant must match `0x800E8948 + 0xEC` = `0x800E8A34`). Do not invent
  a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800E8948\|applyCraftAnimDetailParamsB\|func_800E8948' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c family)
grep -n 'func_800E8948\|applyCraftAnimDetailParamsB' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c
# companion overlays
grep -n '800E8948\|applyCraftAnimDetailParamsB\|func_800E8948' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`playAttachmentCueNoTexture` / next `fake_func_800E8A34`, jal
targets, and the section-4 `ovl_mission` row (base `0x800A5130`).
Companion comment is "per-instance anim/detail setup (sibling of
applyCraftAnimAndDetailParams)" — classify from the body, do not take
the comment as proof.

Expected splits:

- H1: all four sources already `applyCraftAnimDetailParamsB`. Confirm.
- H2: rename the stale placeholder to the human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
or s1792 unwatched-caller Rice recipes. The next 15-title REVISIT
(after this sweep resumes) watches `submitGfxFrame` jal-sites / `$ra`,
not another function-entry PC set.
