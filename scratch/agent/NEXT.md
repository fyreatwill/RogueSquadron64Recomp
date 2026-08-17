# NEXT work unit (s1851)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol sweep. s1850 synchronized leftover
`func_800EFCD4` to `initSoundCueRequest`; last-15 after
s1850 include s1840's M4 REVISIT, so they are not all sweep. Do not
start another M4 instrument this iteration. Do not repeat any
`submitGfxFrame` entry/jal/`prev_pc` recipe.

Exact generated-symbol census for leftover `func_800EFD54`
(`0x800EFD54`, size `0x10`). Companion `mission_overlay.txt` already
names `getSoundCueSubsystemFlag`; generated headers/body/INL
already use that name; TOML still uses the leftover splat name.

Competing hypotheses:

- H1: already synchronized — companion, generated headers/body/INL,
  TOML, and section-4 already agree on `getSoundCueSubsystemFlag`
  and the `0x10` span.
- H2: leftover placeholder — TOML (and/or generated name) is still
  `func_800EFD54` while companion uses `getSoundCueSubsystemFlag`.
- H3: overlay collision or size/boundary disagreement — another
  overlay occupies `0x800EFD54`, or the TOML size is not `0x10`, or
  the generated body is not this function (first insn is not
  `lui $v0, 0x8011`; last is not `jr $ra` / `nop` at
  `0x800EFD5C` / `0x800EFD60`).
- H4: missing companion or generated occupant — no body to rename.

Exact commands:

```
# companion + generated name occupancy
grep -n '800EFD54\|func_800EFD54\|getSoundCueSubsystemFlag' \
  ../rogue_squadron64/symbol_files/mission_overlay.txt \
  ../rogue_squadron64/symbol_files/main_overlay.txt \
  ../rogue_squadron64/symbol_files/*overlay*.txt \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml \
  2>/dev/null | head -80

# live body first/last insns
grep -n 'func_800EFD54\|getSoundCueSubsystemFlag\|0x800EFD54\|0x800EFD5C\|0x800EFD64' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c | head -40
```

Then read the generated function (first/last insns are enough) and
the TOML / section-4 rows. Classify H1–H4 from that table. If H2,
apply the rename in TOML (and generated name only if it is still
stale). Do not invent a new name.

Expected splits:

- H1: all four sources already `getSoundCueSubsystemFlag` / `0x10`.
  No edit. Next leftover `func_800EFD64` (`0x800EFD64`, `0x8`;
  companion `noopHandler_800EFD64`; generated headers/INL already that
  name; TOML still leftover).
- H2: TOML (and/or generated) still `func_800EFD54`. Rename to
  `getSoundCueSubsystemFlag`. Next leftover `func_800EFD64`.
- H3: document the collision or size mismatch; do not rename.
- H4: document the missing occupant; do not invent a name.

Parked M4 (not this iteration): whether a live `0x8000` Y is
clip-rejected at `L_17F0` entry, emitted as a zero-height command,
or emitted on-screen. Command *shape* is closed (s1840
H-standard-edge). Do not re-watch `0x688:0x710`, recapture VMADH,
watch `0x4B7800`, re-walk the ovl20 consumer table, or re-map the
32-byte `0xD60` stores.
