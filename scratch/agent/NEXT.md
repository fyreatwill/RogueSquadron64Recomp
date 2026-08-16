# NEXT work unit (s1677)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 remains in the last-15
titles as the mandatory retail-entry revisit, so this iteration is not
a REVISIT. Candidate: generated `npcProbeDriod` at `0x800CABD4`
(size `0x11CC`). Companion `mission_overlay.txt` already maps
`npcProbeDriod = 0x800CABD4`. Adjacent: previous
`updateProbeDroidHopState` / `0x800CA720`; next TOML `func_800CBDA0`
(`0x800CBDA0`, size `0x29C`; overlay `findNearestNpcWithinRange`).

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
grep -n -C2 '800CABD4\|npcProbeDriod\|800CBDA0\|findNearestNpcWithinRange\|800CA720' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'npcProbeDriod\|func_800CABD4\|findNearestNpcWithinRange\|func_800CBDA0\|updateProbeDroidHopState' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800CABD4\|800CBDA0\|800CA720\|npcProbeDriod\|findNearestNpcWithinRange' \
  syms/rogue_squadron.syms.toml \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: generated function already named `npcProbeDriod`, starts at
  `0x800CABD4`, ends at `0x800CBD9C`/`0x800CBDA0`, TOML size `0x11CC`,
  section-4 `rom_size` matches; only the TOML name changes from a
  placeholder.
- H2: any of those disagree.
- H3: TOML already carries `npcProbeDriod`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `func_800CBDA0` / `findNearestNpcWithinRange`).
