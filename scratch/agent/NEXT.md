# NEXT work unit (s1828)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol sweep. s1824 was the mandatory 15-title
M4 REVISIT (H-rdp-consumer selected); last-15 after s1827 still include
that revisit, so they are not all sweep. Do not start another M4
instrument this iteration. Do not repeat any `submitGfxFrame`
entry/jal/`prev_pc` recipe.

Exact generated-symbol census for leftover `func_800ED200`
(`0x800ED200`, size `0x9B0`). Companion `mission_overlay.txt` already
names `tickActiveSongSlots`; generated headers/body/INL already use
that name; TOML still uses the leftover splat name.

Competing hypotheses:

- H1: already synchronized — companion, generated headers/body/INL,
  TOML, and section-4 already agree on `tickActiveSongSlots` and the
  `0x9B0` span.
- H2: leftover placeholder — TOML (and/or generated name) is still
  `func_800ED200` while companion uses `tickActiveSongSlots`.
- H3: overlay collision or size/boundary disagreement — another
  overlay occupies `0x800ED200`, or the TOML size is not `0x9B0`, or
  the generated body is not this function (first insn is not
  `addiu $sp, $sp, -0x50` / last is not `jr $ra` / `addiu $sp, $sp, 0x50`
  at `0x800EDBA8` / `0x800EDBAC`).
- H4: missing companion or generated occupant — no body to rename.

Exact commands:

```
# companion + generated name occupancy
grep -n '800ED200\|func_800ED200\|tickActiveSongSlots' \
  ../rogue_squadron64/symbol_files/mission_overlay.txt \
  ../rogue_squadron64/symbol_files/main_overlay.txt \
  ../rogue_squadron64/symbol_files/*overlay*.txt \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml \
  2>/dev/null | head -80

# live body first/last insns
grep -n 'func_800ED200\|tickActiveSongSlots\|0x800ED200\|0x800EDBA8\|0x800EDBB0' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c | head -40
```

Then read the generated function (first/last insns and the
`addiu $sp, $sp, -0x50` frame are enough) and the TOML / section-4
rows. Classify H1–H4 from that table. If H2, apply the rename in
TOML (and generated name only if it is still stale). Do not invent
a new name.

Expected splits:

- H1: all four sources already `tickActiveSongSlots` / `0x9B0`.
  No edit. Next leftover `func_800EDBB0` (`0x800EDBB0`, `0xE0`;
  generated headers/INL already `shouldSwitchToPendingSong`; TOML
  still leftover).
- H2: TOML (and/or generated) still `func_800ED200`. Rename to
  `tickActiveSongSlots`. Next leftover `func_800EDBB0`.
- H3: document the collision or size mismatch; do not rename.
- H4: document the missing occupant; do not invent a name.

Parked M4 (not this iteration): RDP command shape of the restaged
`0x670+0x18` XY in the `0xD60` buffer. Do not re-watch `0x688:0x710`,
re-capture VMADH, watch `0x4B7800`, or re-walk the ovl20 consumer
table.
