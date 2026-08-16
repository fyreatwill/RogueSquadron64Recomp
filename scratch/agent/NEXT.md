# NEXT work unit (s1673)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `initNpcActorVariant` at `0x800CA270`
(size `0x134`). Companion `mission_overlay.txt` already maps
`initNpcActorVariant = 0x800CA270`. Adjacent: previous
`playNpcAmbientEffect` / `0x800CA18C` then 4-byte pad
`fake_func_800CA26C` (`0x800CA26C`, size `0x4`); next TOML
`func_800CA3A4` (`0x800CA3A4`, size `0x1BC`, companion
`spawnProbeDroidGroundImpactEffect = 0x800CA3A4`). Skip the pad.

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
grep -n -C2 '800CA270\|initNpcActorVariant\|800CA3A4\|spawnProbeDroidGroundImpactEffect\|800CA26C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'initNpcActorVariant\|func_800CA270\|spawnProbeDroidGroundImpactEffect\|func_800CA3A4\|fake_func_800CA26C\|playNpcAmbientEffect' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800CA270\|800CA3A4\|800CA26C\|initNpcActorVariant\|spawnProbeDroidGroundImpactEffect' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `initNpcActorVariant`, starts at
  `0x800CA270`, ends at `0x800CA3A0`/`0x800CA3A4`, TOML size `0x134`,
  section-4 `rom_size` matches; only TOML name changes from
  `func_800CA270`.
- H2: any of those disagree.
- H3: TOML already carries `initNpcActorVariant`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `func_800CA3A4` / `spawnProbeDroidGroundImpactEffect`).
