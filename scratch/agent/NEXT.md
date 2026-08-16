# NEXT work unit (s1676)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `updateProbeDroidHopState` at
`0x800CA720` (size `0x4B4`). Companion `mission_overlay.txt` already maps
`updateProbeDroidHopState = 0x800CA720`. Adjacent: previous
11→`initProbeDroidScatterLaunch` / `0x800CA560`; next TOML
`npcProbeDriod` (`0x800CABD4`, size `0x11CC`, companion same name).

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
grep -n -C2 '800CA720\|updateProbeDroidHopState\|800CABD4\|npcProbeDriod\|800CA560' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'updateProbeDroidHopState\|func_800CA720\|npcProbeDriod\|func_800CABD4\|initProbeDroidScatterLaunch' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800CA720\|800CABD4\|800CA560\|updateProbeDroidHopState\|npcProbeDriod' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `updateProbeDroidHopState`,
  starts at `0x800CA720`, ends at `0x800CABD0`/`0x800CABD4`, TOML size
  `0x4B4`, section-4 `rom_size` matches; only TOML name changes from
  `func_800CA720`.
- H2: any of those disagree.
- H3: TOML already carries `updateProbeDroidHopState`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `npcProbeDriod` / `0x800CABD4`).
