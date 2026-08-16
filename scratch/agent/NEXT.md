# NEXT work unit (s1681)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `func_800CC2AC` /
`tickAtAtBodyTransform` at `0x800CC2AC` (size `0x70C`). Companion
`mission_overlay.txt` already maps `tickAtAtBodyTransform =
0x800CC2AC`. Adjacent: previous `tickActorTexturedSoundEffect` /
`0x800CC158`; next TOML `func_800CC9B8` (`0x800CC9B8`, size `0x164`;
overlay `tickAtAtAudioAndWeaponState`).

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
grep -n -C2 '800CC2AC\|tickAtAtBodyTransform\|800CC9B8\|tickAtAtAudioAndWeaponState\|800CC158' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'tickAtAtBodyTransform\|func_800CC2AC\|tickAtAtAudioAndWeaponState\|func_800CC9B8\|tickActorTexturedSoundEffect' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800CC2AC\|800CC9B8\|800CC158\|tickAtAtBodyTransform\|tickAtAtAudioAndWeaponState' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `tickAtAtBodyTransform`,
  starts at `0x800CC2AC`, ends at `0x800CC9B4`/`0x800CC9B8`, TOML size
  `0x70C`, section-4 `rom_size` matches; only the TOML name changes
  from `func_800CC2AC`.
- H2: any of those disagree.
- H3: TOML already carries `tickAtAtBodyTransform`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `func_800CC9B8` / `tickAtAtAudioAndWeaponState`).
