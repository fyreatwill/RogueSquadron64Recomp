# NEXT work unit (s1854)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol sweep. s1853 synchronized leftover
`func_800EFD6C` to `noopHandler`; last-15 after s1853 include
s1840's M4 REVISIT, so they are not all sweep. Do not start
another M4 instrument this iteration. Do not repeat any
`submitGfxFrame` entry/jal/`prev_pc` recipe.

Exact generated-symbol census for leftover `fake_func_800EFD74`
(`0x800EFD74`, size `0xC`). Companion `mission_overlay.txt`
already names `fake_func_800EFD74`; generated headers/body/INL
and TOML already use that name.

Competing hypotheses:

- H1: already synchronized — companion, generated headers/body/INL,
  TOML, and section-4 already agree on `fake_func_800EFD74`
  and the `0xC` span.
- H2: leftover placeholder — TOML (and/or generated name) is still
  `func_800EFD74` while companion uses `fake_func_800EFD74`.
- H3: overlay collision or size/boundary disagreement — another
  overlay occupies `0x800EFD74`, or the TOML size is not `0xC`, or
  the generated body is not this function (first insn is not
  `srl $v1, $v0, 2`; last is not `lw $v0, 0xBC($fp)` at
  `0x800EFD7C`).
- H4: missing companion or generated occupant — no body to rename.

Exact commands:

```
# companion + generated name occupancy
grep -n '800EFD74\|func_800EFD74\|fake_func_800EFD74' \
  ../rogue_squadron64/symbol_files/mission_overlay.txt \
  ../rogue_squadron64/symbol_files/main_overlay.txt \
  ../rogue_squadron64/symbol_files/*overlay*.txt \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml \
  2>/dev/null | head -80

# live body first/last insns
grep -n 'func_800EFD74\|fake_func_800EFD74\|0x800EFD74\|0x800EFD78\|0x800EFD7C\|0x800EFD80' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c | head -40
```

Then read the generated function (first/last insns are enough) and
the TOML / section-4 rows. Classify H1–H4 from that table. If H2,
apply the rename in TOML (and generated name only if it is still
stale). Do not invent a new name. Companion name is
`fake_func_800EFD74`.

Expected splits:

- H1: all four sources already `fake_func_800EFD74` / `0xC`.
  No edit. Next leftover `func_800EFD80` (`0x800EFD80`, `0x5C`;
  companion `dispatchSlotAction5IfActive`; generated
  headers/INL already that name; TOML still leftover).
- H2: TOML (and/or generated) still `func_800EFD74`. Rename to
  `fake_func_800EFD74`. Next leftover `func_800EFD80` as above.
- H3: document the collision or size mismatch; do not rename.
- H4: document the missing occupant; do not invent a name.

Parked M4 (not this iteration): whether a live `0x8000` Y is
clip-rejected at `L_17F0` entry, emitted as a zero-height command,
or emitted on-screen. Command *shape* is closed (s1840
H-standard-edge). Do not re-watch `0x688:0x710`, recapture VMADH,
watch `0x4B7800`, re-walk the ovl20 consumer table, or re-map the
32-byte `0xD60` stores.
