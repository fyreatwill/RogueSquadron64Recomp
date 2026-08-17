# NEXT work unit (s1853)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol sweep. s1852 synchronized leftover
`func_800EFD64` to `noopHandler_800EFD64`; last-15 after
s1852 include s1840's M4 REVISIT, so they are not all sweep. Do not
start another M4 instrument this iteration. Do not repeat any
`submitGfxFrame` entry/jal/`prev_pc` recipe.

Exact generated-symbol census for leftover `func_800EFD6C`
(`0x800EFD6C`, size `0x8`). Companion `mission_overlay.txt` already
names `noopHandler`; generated headers/body/INL already
use that name; TOML still uses the leftover splat name.

Competing hypotheses:

- H1: already synchronized — companion, generated headers/body/INL,
  TOML, and section-4 already agree on `noopHandler`
  and the `0x8` span.
- H2: leftover placeholder — TOML (and/or generated name) is still
  `func_800EFD6C` while companion uses `noopHandler`.
- H3: overlay collision or size/boundary disagreement — another
  overlay occupies `0x800EFD6C`, or the TOML size is not `0x8`, or
  the generated body is not this function (first insn is not
  `jr $ra`; last is not `nop` at `0x800EFD70`).
- H4: missing companion or generated occupant — no body to rename.

Exact commands:

```
# companion + generated name occupancy
grep -n '800EFD6C\|func_800EFD6C\|noopHandler' \
  ../rogue_squadron64/symbol_files/mission_overlay.txt \
  ../rogue_squadron64/symbol_files/main_overlay.txt \
  ../rogue_squadron64/symbol_files/*overlay*.txt \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml \
  2>/dev/null | head -80

# live body first/last insns
grep -n 'func_800EFD6C\|noopHandler\|0x800EFD6C\|0x800EFD70\|0x800EFD74' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c | head -40
```

Then read the generated function (first/last insns are enough) and
the TOML / section-4 rows. Classify H1–H4 from that table. If H2,
apply the rename in TOML (and generated name only if it is still
stale). Do not invent a new name. Companion name is `noopHandler`
(not `noopHandler_800EFD6C`).

Expected splits:

- H1: all four sources already `noopHandler` / `0x8`.
  No edit. Next leftover `fake_func_800EFD74` (`0x800EFD74`, `0xC`;
  companion and generated already that name; TOML already
  `fake_func_800EFD74`) or leftover `func_800EFD80` (`0x800EFD80`,
  `0x5C`; companion `dispatchSlotAction5IfActive`; generated
  headers/INL already that name; TOML still leftover).
- H2: TOML (and/or generated) still `func_800EFD6C`. Rename to
  `noopHandler`. Next leftover `fake_func_800EFD74` or
  `func_800EFD80` as above.
- H3: document the collision or size mismatch; do not rename.
- H4: document the missing occupant; do not invent a name.

Parked M4 (not this iteration): whether a live `0x8000` Y is
clip-rejected at `L_17F0` entry, emitted as a zero-height command,
or emitted on-screen. Command *shape* is closed (s1840
H-standard-edge). Do not re-watch `0x688:0x710`, recapture VMADH,
watch `0x4B7800`, re-walk the ovl20 consumer table, or re-map the
32-byte `0xD60` stores.
