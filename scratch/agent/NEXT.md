# NEXT work unit (s1680)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `func_800CC158` /
`tickActorTexturedSoundEffect` at `0x800CC158` (size `0x154`). Companion
`mission_overlay.txt` already maps `tickActorTexturedSoundEffect =
0x800CC158`. Adjacent: previous `initActorFromSpawnTemplate` /
`0x800CC03C`; next TOML `func_800CC2AC` (`0x800CC2AC`, size `0x70C`;
overlay `tickAtAtBodyTransform`).

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
grep -n -C2 '800CC158\|tickActorTexturedSoundEffect\|800CC2AC\|tickAtAtBodyTransform\|800CC03C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'tickActorTexturedSoundEffect\|func_800CC158\|tickAtAtBodyTransform\|func_800CC2AC\|initActorFromSpawnTemplate' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800CC158\|800CC2AC\|800CC03C\|tickActorTexturedSoundEffect\|tickAtAtBodyTransform' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `tickActorTexturedSoundEffect`,
  starts at `0x800CC158`, ends at `0x800CC2A8`/`0x800CC2AC`, TOML size
  `0x154`, section-4 `rom_size` matches; only the TOML name changes
  from `func_800CC158`.
- H2: any of those disagree.
- H3: TOML already carries `tickActorTexturedSoundEffect`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `func_800CC2AC` / `tickAtAtBodyTransform`).
