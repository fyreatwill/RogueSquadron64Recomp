# NEXT work unit (s1810)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `func_800EB984`. Last-15 ledger titles after s1809
include the s1808 revisit (`selected H2 menuIn/mission jal-sites`), so
the 15-title all-sweep REVISIT gate does not fire.

Census leftover `func_800EB984` (`0x800EB984`). Neighbor peek already:
TOML still carries `{ name = "func_800EB984", vram = 0x800EB984, size = 0xC }`;
generated `funcs.h` / `funcs_39.c` / overlay INL and companion
`mission_overlay.txt` already use `resetObjectPoolListHead` (first insn
`lui $v0, 0x8011` at `0x800EB984`; last live `jr $ra` / `sw $zero,
-0x3F40($v0)` at `0x800EB988`/`0x800EB98C` writing `0x8010C0C0`;
section-4 `.offset = 0x00046854`, `.rom_size = 0x0000000C`). Previous
`npcAtPtUpdate` occupies `0x800EA5E0` size `0x13A4` (s1809 confirmed).
Next occupant `npcPowerUpUpdate` starts at `0x800EB990`. One generated
`jal 0x800EB984` inside `resetObjectContextPool` already dispatches
the human name.

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay INL,
  and companion all agree on `resetObjectPoolListHead` with matching size
  (confirm only; no rename).
- H2: one source still carries a stale `func_800EB984` placeholder.
  Fix the stale source (do not invent a name).
- H3: leftover splat, overlay collision, or size/boundary disagreement
  (previous `npcAtPtUpdate` ends at `0x800EB984`; generated next occupant
  is `npcPowerUpUpdate` at `0x800EB990`). Do not invent a name.
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800EB984\|func_800EB984\|resetObjectPoolListHead\|800EB990\|npcPowerUpUpdate' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body (funcs_39.c / funcs_40.c family)
grep -n 'resetObjectPoolListHead\|func_800EB984\|npcPowerUpUpdate' \
  ../N64Recomp/RecompiledFuncs/funcs_3*.c \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800EB984\|func_800EB984\|resetObjectPoolListHead\|800EB990\|npcPowerUpUpdate' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: first/last insn, previous
`npcAtPtUpdate` / next `npcPowerUpUpdate`, the `jal 0x800EB984` site
in `resetObjectContextPool`, and the section-4 `ovl_mission` row
(base `0x800A5130`). Classify the three-instruction store-zero; do
not invent a name if the body does not match the existing
generated/companion name.

Expected splits:

- H1: all four sources already `resetObjectPoolListHead` at size `0xC`.
  Confirm.
- H2: rename the stale `func_800EB984` placeholder to match the
  generated/companion human name.
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776 main-text,
s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice recipes. The next
15-title REVISIT is the M4 accumulator boundary, not another
`submitGfxFrame` PC set.
