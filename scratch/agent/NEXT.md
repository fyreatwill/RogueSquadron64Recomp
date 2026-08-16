# NEXT work unit (s1672)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `playNpcAmbientEffect` at `0x800CA18C`
(size `0xE0`). Companion `mission_overlay.txt` already maps
`playNpcAmbientEffect = 0x800CA18C`. Adjacent: previous
`npcTurretUpdate` / `0x800C8F90`; next TOML `fake_func_800CA26C`
(`0x800CA26C`, size `0x4`) then `func_800CA270` (companion
`initNpcActorVariant = 0x800CA270`).

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
grep -n -C2 '800CA18C\|playNpcAmbientEffect\|800CA26C\|800CA270\|initNpcActorVariant' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'playNpcAmbientEffect\|func_800CA18C\|initNpcActorVariant\|func_800CA270\|fake_func_800CA26C\|npcTurretUpdate' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800CA18C\|800CA26C\|800CA270\|playNpcAmbientEffect\|initNpcActorVariant' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `playNpcAmbientEffect`, ends at
  `0x800CA268`/`0x800CA26C`, TOML size `0xE0`, section-4 `rom_size`
  matches; only TOML name changes from `func_800CA18C`.
- H2: any of those disagree.
- H3: TOML already carries `playNpcAmbientEffect`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `fake_func_800CA26C` then `func_800CA270` /
`initNpcActorVariant`).
