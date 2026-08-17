# NEXT work unit (s1825)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol sweep. s1824 was the mandatory 15-title
M4 REVISIT (H-rdp-consumer selected); last-15 after s1824 are not
all sweep. Do not start another M4 instrument this iteration.
Do not repeat any `submitGfxFrame` entry/jal/`prev_pc` recipe.

Exact generated-symbol census for leftover `func_800ECE10`
(`0x800ECE10`, size `0x338`). Companion `mission_overlay.txt` and
generated headers/body/INL already use `datItemActorNpcHandler`;
TOML is still leftover.

Competing hypotheses:

- H1: already synchronized — companion, generated headers/body/INL,
  TOML, and section-4 already agree on one name and the `0x338` span.
- H2: leftover placeholder — TOML (and/or generated name) is still
  `func_800ECE10` while companion and the live body are
  `datItemActorNpcHandler`; rename TOML (and generated name if stale)
  to match.
- H3: overlay collision or size/boundary disagreement — another
  overlay occupies `0x800ECE10`, or the TOML size is not `0x338`, or
  the generated body is not this kernel (prologue is not
  `addiu $sp, $sp, -0x140` / last `jr $ra` + `addiu $sp, $sp, 0x140`
  at `0x800ED140` / `0x800ED144`).
- H4: missing companion or generated occupant — no body to rename.

Exact commands:

```
# companion + generated name occupancy
grep -n '800ECE10\|datItemActorNpcHandler\|func_800ECE10\|fake_func_800ECE10' \
  ../rogue_squadron64/config/symbol_addrs_overlays.txt \
  ../rogue_squadron64/config/*overlay*.txt \
  RecompiledFuncs/funcs.h RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml \
  2>/dev/null | head -80

# live body first/last insns and jal sites
grep -n 'datItemActorNpcHandler\|func_800ECE10\|0x800ECE10' \
  RecompiledFuncs/funcs_*.c | head -40
```

Then read the generated function (first ~40 and last ~20 lines) and
the TOML / section-4 rows. Classify H1–H4 from that table. If H2,
apply the rename in TOML (and generated name only if it is still
the leftover). Do not invent a new name.

Expected splits:

- H1: all four sources already `datItemActorNpcHandler` / `0x338`.
  No edit. Next leftover `fake_func_800ED148` (`0x800ED148`, `0x8`).
- H2: TOML (and/or generated) still `func_800ECE10`. Rename to
  `datItemActorNpcHandler`. Next leftover `fake_func_800ED148`.
- H3: document the collision or size mismatch; do not rename.
- H4: document the missing occupant; do not invent a name.

Parked M4 (not this iteration): RDP command shape of the restaged
`0x670+0x18` XY in the `0xD60` buffer. Do not re-watch `0x688:0x710`,
re-capture VMADH, watch `0x4B7800`, or re-walk the ovl20 consumer
table.
