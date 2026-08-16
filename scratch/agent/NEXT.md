# NEXT work unit (s1679)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `func_800CC03C` /
`initActorFromSpawnTemplate` at `0x800CC03C` (size `0x11C`). Companion
`mission_overlay.txt` already maps `initActorFromSpawnTemplate =
0x800CC03C`. Adjacent: previous `findNearestNpcWithinRange` /
`0x800CBDA0`; next TOML `func_800CC158` (`0x800CC158`, size `0x154`;
overlay `tickActorTexturedSoundEffect`).

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
grep -n -C2 '800CC03C\|initActorFromSpawnTemplate\|800CC158\|tickActorTexturedSoundEffect\|800CBDA0' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'initActorFromSpawnTemplate\|func_800CC03C\|tickActorTexturedSoundEffect\|func_800CC158\|findNearestNpcWithinRange' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800CC03C\|800CC158\|800CBDA0\|initActorFromSpawnTemplate\|tickActorTexturedSoundEffect' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `initActorFromSpawnTemplate`,
  starts at `0x800CC03C`, ends at `0x800CC154`/`0x800CC158`, TOML size
  `0x11C`, section-4 `rom_size` matches; only the TOML name changes
  from `func_800CC03C`.
- H2: any of those disagree.
- H3: TOML already carries `initActorFromSpawnTemplate`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `func_800CC158` / `tickActorTexturedSoundEffect`).
