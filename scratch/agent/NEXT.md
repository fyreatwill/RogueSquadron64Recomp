# NEXT work unit (s1667)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. s1666 was the mandatory
retail-entry revisit, so the last-15 titles are no longer all
sweep-scoped. Candidate: generated `spawnNpcDestructionEffect` / TOML
`func_800C8178` at `0x800C8178` (size `0x38C`). Companion
`mission_overlay.txt` already maps `spawnNpcDestructionEffect = 0x800C8178`.
Adjacent: previous `playNpcStateChangeEffect` / `0x800C7FF8`; next TOML
`func_800C8504` at `0x800C8504`.

Competing hypotheses and discriminator:

- H1: companion mapping, live generated body/name, previous and next
  VRAM boundaries, TOML size, and overlay section-4 span all agree;
  only the TOML name is a stale `func_800C8178` placeholder — correct it.
- H2: a source disagrees (size, overlay span, companion name, or
  generated body semantics) — leave unsynchronized or split; do not
  invent a name.
- H3: already fully synchronized across all sources — confirm and
  advance to the next placeholder.

Discriminator: one static comparison, no game run.

```sh
# companion
grep -n -C2 '800C8178\|spawnNpcDestructionEffect\|800C8504' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt
# generated body + adjacent
grep -n 'spawnNpcDestructionEffect\|func_800C8178\|func_800C8504\|playNpcStateChangeEffect' \
  RecompiledFuncs/funcs_*.c | head
# TOML + overlay tables
grep -n '800C8178\|800C8504\|spawnNpcDestructionEffect' \
  syms/rogue_squadron.syms.toml overlays/*.toml 2>/dev/null
```

Expected splits:

- H1: generated function already named `spawnNpcDestructionEffect`,
  ends at `0x800C8500`/`0x800C8504`, TOML size `0x38C`, section-4
  `rom_size` matches; only TOML name changes.
- H2: any of those disagree.
- H3: TOML already carries `spawnNpcDestructionEffect`.

Do not start another retail-entry experiment this iteration.
After this census, the next candidate is whatever the next boundary
is (likely `func_800C8504`).
