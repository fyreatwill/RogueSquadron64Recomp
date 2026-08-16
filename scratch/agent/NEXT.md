# NEXT work unit (s1670)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `setupNpcModelForState` / TOML
`func_800C8E90` at `0x800C8E90` (size `0x100`). Companion
`mission_overlay.txt` already maps `setupNpcModelForState = 0x800C8E90`.
Adjacent: previous `updateNpcOrientationFromMotion` / `0x800C8978`; next
TOML `npcTurretUpdate` at `0x800C8F90` (companion also `npcTurretUpdate`).

Competing hypotheses and discriminator:

- H1: companion mapping, live generated body/name, previous and next
  VRAM boundaries, TOML size, and overlay section-4 span all agree;
  only the TOML name is a stale `func_800C8E90` placeholder — correct it.
- H2: a source disagrees (size, overlay span, companion name, or
  generated body semantics) — leave unsynchronized or split; do not
  invent a name.
- H3: already fully synchronized across all sources — confirm and
  advance to the next placeholder.

Discriminator: one static comparison, no game run.

```sh
# companion
grep -n -C2 '800C8E90\|setupNpcModelForState\|800C8F90\|npcTurretUpdate' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'setupNpcModelForState\|func_800C8E90\|npcTurretUpdate\|updateNpcOrientationFromMotion' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800C8E90\|800C8F90\|setupNpcModelForState\|npcTurretUpdate' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `setupNpcModelForState`,
  ends at `0x800C8F8C`/`0x800C8F90`, TOML size `0x100`, section-4
  `rom_size` matches; only TOML name changes.
- H2: any of those disagree.
- H3: TOML already carries `setupNpcModelForState`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `npcTurretUpdate` / `0x800C8F90`, or the next stale
placeholder after it).
