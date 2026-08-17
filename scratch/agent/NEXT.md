# NEXT work unit (s1847)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the generated-symbol sweep. s1846 synchronized leftover
`func_800EFB40` to `stopMusicAndResetAudio`; last-15 after
s1846 include s1840's M4 REVISIT, so they are not all sweep. Do not
start another M4 instrument this iteration. Do not repeat any
`submitGfxFrame` entry/jal/`prev_pc` recipe.

Exact generated-symbol census for leftover `func_800EFB94`
(`0x800EFB94`, size `0x20`). Companion `mission_overlay.txt` already
names `preloadSceneSongsWrapper`; generated headers/body/INL already
use that name; TOML still uses the leftover splat name.

Competing hypotheses:

- H1: already synchronized — companion, generated headers/body/INL,
  TOML, and section-4 already agree on `preloadSceneSongsWrapper` and
  the `0x20` span.
- H2: leftover placeholder — TOML (and/or generated name) is still
  `func_800EFB94` while companion uses `preloadSceneSongsWrapper`.
- H3: overlay collision or size/boundary disagreement — another
  overlay occupies `0x800EFB94`, or the TOML size is not `0x20`, or
  the generated body is not this function (first insn is not
  `addiu $sp, $sp, -0x18` then `jal preloadSceneReferencedSongs` /
  `0x800EEA54`; last is not `jr $ra` / `addiu $sp, $sp, 0x18` at
  `0x800EFBAC` / `0x800EFBB0`).
- H4: missing companion or generated occupant — no body to rename.

Exact commands:

```
# companion + generated name occupancy
grep -n '800EFB94\|func_800EFB94\|preloadSceneSongsWrapper' \
  ../rogue_squadron64/symbol_files/mission_overlay.txt \
  ../rogue_squadron64/symbol_files/main_overlay.txt \
  ../rogue_squadron64/symbol_files/*overlay*.txt \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  syms/rogue_squadron.syms.toml \
  2>/dev/null | head -80

# live body first/last insns
grep -n 'func_800EFB94\|preloadSceneSongsWrapper\|0x800EFB94\|0x800EFBAC\|0x800EFBB4' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c | head -40
```

Then read the generated function (first/last insns are enough) and
the TOML / section-4 rows. Classify H1–H4 from that table. If H2,
apply the rename in TOML (and generated name only if it is still
stale). Do not invent a new name.

Expected splits:

- H1: all four sources already `preloadSceneSongsWrapper` / `0x20`.
  No edit. Next leftover `func_800EFBB4` (`0x800EFBB4`, `0xD0`;
  generated headers/INL already `commitStagedSongAndPlay`; TOML
  still leftover).
- H2: TOML (and/or generated) still `func_800EFB94`. Rename to
  `preloadSceneSongsWrapper`. Next leftover `func_800EFBB4`.
- H3: document the collision or size mismatch; do not rename.
- H4: document the missing occupant; do not invent a name.

Parked M4 (not this iteration): whether a live `0x8000` Y is
clip-rejected at `L_17F0` entry, emitted as a zero-height command,
or emitted on-screen. Command *shape* is closed (s1840
H-standard-edge). Do not re-watch `0x688:0x710`, recapture VMADH,
watch `0x4B7800`, re-walk the ovl20 consumer table, or re-map the
32-byte `0xD60` stores.
