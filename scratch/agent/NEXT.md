# NEXT work unit (s1675)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `initProbeDroidScatterLaunch` at
`0x800CA560` (size `0x1C0`). Companion `mission_overlay.txt` already maps
`initProbeDroidScatterLaunch = 0x800CA560`. Adjacent: previous
`spawnProbeDroidGroundImpactEffect` / `0x800CA3A4`; next TOML
`func_800CA720` (`0x800CA720`, size `0x4B4`, companion
`updateProbeDroidHopState = 0x800CA720`).

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
grep -n -C2 '800CA560\|initProbeDroidScatterLaunch\|800CA720\|updateProbeDroidHopState\|800CA3A4' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'initProbeDroidScatterLaunch\|func_800CA560\|updateProbeDroidHopState\|func_800CA720\|spawnProbeDroidGroundImpactEffect' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800CA560\|800CA720\|800CA3A4\|initProbeDroidScatterLaunch\|updateProbeDroidHopState' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `initProbeDroidScatterLaunch`,
  starts at `0x800CA560`, ends at `0x800CA71C`/`0x800CA720`, TOML size
  `0x1C0`, section-4 `rom_size` matches; only TOML name changes from
  `func_800CA560`.
- H2: any of those disagree.
- H3: TOML already carries `initProbeDroidScatterLaunch`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `func_800CA720` / `updateProbeDroidHopState`).
