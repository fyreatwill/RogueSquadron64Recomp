# NEXT work unit (s1826)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol sweep. s1824 was the mandatory 15-title
M4 REVISIT (H-rdp-consumer selected); last-15 after s1825 still include
that revisit, so they are not all sweep. Do not start another M4
instrument this iteration. Do not repeat any `submitGfxFrame`
entry/jal/`prev_pc` recipe.

Exact generated-symbol census for leftover `fake_func_800ED148`
(`0x800ED148`, size `0x8`). Companion `mission_overlay.txt`, generated
headers/body/INL, and TOML already use the leftover splat name.

Competing hypotheses:

- H1: already synchronized — companion, generated headers/body/INL,
  TOML, and section-4 already agree on the leftover name and the `0x8`
  span.
- H2: leftover placeholder — TOML (and/or generated name) is still
  `func_800ED148` while companion uses `fake_func_800ED148`, or a
  companion human name exists that generated/TOML have not taken.
- H3: overlay collision or size/boundary disagreement — another
  overlay occupies `0x800ED148`, or the TOML size is not `0x8`, or
  the generated body is not this two-insn leftover (first insn is not
  `lui $at, 0x801F` / last is not `addu $at, $at, $v1` at
  `0x800ED14C`).
- H4: missing companion or generated occupant — no body to rename.

Exact commands:

```
# companion + generated name occupancy
grep -n '800ED148\|fake_func_800ED148\|func_800ED148' \
  ../rogue_squadron64/symbol_files/mission_overlay.txt \
  ../rogue_squadron64/symbol_files/*overlay*.txt \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml \
  2>/dev/null | head -80

# live body first/last insns
grep -n 'fake_func_800ED148\|func_800ED148\|0x800ED148' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c | head -40
```

Then read the generated function (the whole body is ~10 lines) and
the TOML / section-4 rows. Classify H1–H4 from that table. If H2,
apply the rename in TOML (and generated name only if it is still
stale). Do not invent a new name.

Expected splits:

- H1: all four sources already `fake_func_800ED148` / `0x8`.
  No edit. Next leftover `func_800ED150` (`0x800ED150`, `0xB0`;
  companion `main_overlay.txt` already names
  `claimSongSlotForCurrentHandle`; mission overlay and generated
  still leftover).
- H2: TOML (and/or generated) still `func_800ED148`, or a companion
  human name exists unused. Rename to the companion name. Next leftover
  `func_800ED150`.
- H3: document the collision or size mismatch; do not rename.
- H4: document the missing occupant; do not invent a name.

Parked M4 (not this iteration): RDP command shape of the restaged
`0x670+0x18` XY in the `0xD60` buffer. Do not re-watch `0x688:0x710`,
re-capture VMADH, watch `0x4B7800`, or re-walk the ovl20 consumer
table.
