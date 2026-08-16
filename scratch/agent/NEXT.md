# NEXT work unit (s1678)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `func_800CBDA0` /
`findNearestNpcWithinRange` at `0x800CBDA0` (size `0x29C`). Companion
`mission_overlay.txt` already maps `findNearestNpcWithinRange =
0x800CBDA0`. Adjacent: previous `npcProbeDriod` / `0x800CABD4`; next
TOML `func_800CC03C` (`0x800CC03C`, size `0x11C`; overlay
`initActorFromSpawnTemplate`).

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
grep -n -C2 '800CBDA0\|findNearestNpcWithinRange\|800CC03C\|initActorFromSpawnTemplate\|800CABD4' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'findNearestNpcWithinRange\|func_800CBDA0\|initActorFromSpawnTemplate\|func_800CC03C\|npcProbeDriod' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800CBDA0\|800CC03C\|800CABD4\|findNearestNpcWithinRange\|initActorFromSpawnTemplate' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `findNearestNpcWithinRange`,
  starts at `0x800CBDA0`, ends at `0x800CC038`/`0x800CC03C`, TOML size
  `0x29C`, section-4 `rom_size` matches; only the TOML name changes
  from `func_800CBDA0`.
- H2: any of those disagree.
- H3: TOML already carries `findNearestNpcWithinRange`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `func_800CC03C` / `initActorFromSpawnTemplate`).
