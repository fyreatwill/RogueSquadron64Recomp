# NEXT work unit (s1671)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `npcTurretUpdate` at `0x800C8F90`
(size `0x11FC`). Companion `mission_overlay.txt` already maps
`npcTurretUpdate = 0x800C8F90`. Adjacent: previous
`setupNpcModelForState` / `0x800C8E90`; next TOML `func_800CA18C`
(companion `playNpcAmbientEffect = 0x800CA18C`).

Competing hypotheses and discriminator:

- H1: companion mapping, live generated body/name, previous and next
  VRAM boundaries, TOML size, and overlay section-4 span all agree;
  only the TOML name is a stale placeholder — correct it.
- H2: a source disagrees (size, overlay span, companion name, or
  generated body semantics) — leave unsynchronized or split; do not
  invent a name.
- H3: already fully synchronized across all sources — confirm and
  advance to the next placeholder.

Discriminator: one static comparison, no game run.

```sh
# companion
grep -n -C2 '800C8F90\|npcTurretUpdate\|800CA18C\|playNpcAmbientEffect' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'npcTurretUpdate\|func_800C8F90\|playNpcAmbientEffect\|func_800CA18C\|setupNpcModelForState' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800C8F90\|800CA18C\|npcTurretUpdate\|playNpcAmbientEffect' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `npcTurretUpdate`, ends at
  `0x800CA188`/`0x800CA18C`, TOML size `0x11FC`, section-4 `rom_size`
  matches; only TOML name changes.
- H2: any of those disagree.
- H3: TOML already carries `npcTurretUpdate`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `func_800CA18C` / `playNpcAmbientEffect`).
