# NEXT work unit (s1855)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol sweep. s1854 confirmed leftover
`fake_func_800EFD74` (H1); last-15 after s1854 include s1840's
M4 REVISIT, so they are not all sweep. Do not start another M4
instrument this iteration. Do not repeat any `submitGfxFrame`
entry/jal/`prev_pc` recipe.

Exact generated-symbol census for leftover `func_800EFD80`
(`0x800EFD80`, size `0x5C`). Companion `mission_overlay.txt`
already names `dispatchSlotAction5IfActive`; generated
headers/body/INL already use that name; TOML still leftover
`func_800EFD80`.

Competing hypotheses:

- H1: already synchronized — companion, generated headers/body/INL,
  TOML, and section-4 already agree on `dispatchSlotAction5IfActive`
  and the `0x5C` span.
- H2: leftover placeholder — TOML (and/or generated name) is still
  `func_800EFD80` while companion uses `dispatchSlotAction5IfActive`.
- H3: overlay collision or size/boundary disagreement — another
  overlay occupies `0x800EFD80`, or the TOML size is not `0x5C`, or
  the generated body is not this function (first insn is not
  `addiu $sp, $sp, -0x28`; last is not `jr $ra` / `addiu $sp, $sp, 0x28`
  at `0x800EFDD4` / `0x800EFDD8`).
- H4: missing companion or generated occupant — no body to rename.

Exact commands:

```
# companion + generated name occupancy
grep -n '800EFD80\|func_800EFD80\|dispatchSlotAction5IfActive' \
  ../rogue_squadron64/symbol_files/mission_overlay.txt \
  ../rogue_squadron64/symbol_files/main_overlay.txt \
  ../rogue_squadron64/symbol_files/*overlay*.txt \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml \
  2>/dev/null | head -80

# live body first/last insns
grep -n 'func_800EFD80\|dispatchSlotAction5IfActive\|0x800EFD80\|0x800EFDD4\|0x800EFDD8\|0x800EFDDC' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c | head -40
```

Then read the generated function (first/last insns are enough) and
the TOML / section-4 rows. Classify H1–H4 from that table. If H2,
apply the rename in TOML (and generated name only if it is still
stale). Do not invent a new name. Companion name is
`dispatchSlotAction5IfActive`.

Expected splits:

- H1: all four sources already `dispatchSlotAction5IfActive` / `0x5C`.
  No edit. Next leftover `fake_func_800EFDDC` (`0x800EFDDC`, `0x4`).
- H2: TOML (and/or generated) still `func_800EFD80`. Rename to
  `dispatchSlotAction5IfActive`. Next leftover `fake_func_800EFDDC`
  as above.
- H3: document the collision or size mismatch; do not rename.
- H4: document the missing occupant; do not invent a name.

Parked M4 (not this iteration): whether a live `0x8000` Y is
clip-rejected at `L_17F0` entry, emitted as a zero-height command,
or emitted on-screen. Command *shape* is closed (s1840
H-standard-edge). Do not re-watch `0x688:0x710`, recapture VMADH,
watch `0x4B7800`, re-walk the ovl20 consumer table, or re-map the
32-byte `0xD60` stores.
