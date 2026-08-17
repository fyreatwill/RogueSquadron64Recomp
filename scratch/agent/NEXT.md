# NEXT work unit (s1832)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol sweep. s1824 was the mandatory 15-title
M4 REVISIT (H-rdp-consumer selected); last-15 after s1831 still include
that revisit, so they are not all sweep. Do not start another M4
instrument this iteration. Do not repeat any `submitGfxFrame`
entry/jal/`prev_pc` recipe.

Exact generated-symbol census for leftover `func_800EDF68`
(`0x800EDF68`, size `0x7C8`). Companion `mission_overlay.txt` already
names `processPendingSoundCueRequest`; generated headers/body/INL
already use that name; TOML still uses the leftover splat name.

Competing hypotheses:

- H1: already synchronized — companion, generated headers/body/INL,
  TOML, and section-4 already agree on `processPendingSoundCueRequest`
  and the `0x7C8` span.
- H2: leftover placeholder — TOML (and/or generated name) is still
  `func_800EDF68` while companion uses `processPendingSoundCueRequest`.
- H3: overlay collision or size/boundary disagreement — another
  overlay occupies `0x800EDF68`, or the TOML size is not `0x7C8`, or
  the generated body is not this function (first insn is not
  `lui $v0, 0x8011` / last is not `jr $ra` / `addiu $sp, $sp, 0x50`
  at `0x800EE728` / `0x800EE72C`).
- H4: missing companion or generated occupant — no body to rename.

Exact commands:

```
# companion + generated name occupancy
grep -n '800EDF68\|func_800EDF68\|processPendingSoundCueRequest' \
  ../rogue_squadron64/symbol_files/mission_overlay.txt \
  ../rogue_squadron64/symbol_files/main_overlay.txt \
  ../rogue_squadron64/symbol_files/*overlay*.txt \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml \
  2>/dev/null | head -80

# live body first/last insns
grep -n 'func_800EDF68\|processPendingSoundCueRequest\|0x800EDF68\|0x800EE728\|0x800EE730' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c | head -40
```

Then read the generated function (first/last insns are enough) and
the TOML / section-4 rows. Classify H1–H4 from that table. If H2,
apply the rename in TOML (and generated name only if it is still
stale). Do not invent a new name.

Expected splits:

- H1: all four sources already `processPendingSoundCueRequest` /
  `0x7C8`. No edit. Next leftover `func_800EE730` (`0x800EE730`,
  `0x254`; generated headers/INL already `tickSongFadeTimer`; TOML
  still leftover).
- H2: TOML (and/or generated) still `func_800EDF68`. Rename to
  `processPendingSoundCueRequest`. Next leftover `func_800EE730`.
- H3: document the collision or size mismatch; do not rename.
- H4: document the missing occupant; do not invent a name.

Parked M4 (not this iteration): RDP command shape of the restaged
`0x670+0x18` XY in the `0xD60` buffer. Do not re-watch `0x688:0x710`,
re-capture VMADH, watch `0x4B7800`, or re-walk the ovl20 consumer
table.
