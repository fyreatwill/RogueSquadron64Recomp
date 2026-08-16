# NEXT work unit (s1653)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. The next candidate is
`func_800C7978`, independently named `spawnEffectOnNamedDatItem` at
`0x800C7978` (size `0x78`). Generated already uses the human name; TOML still
carries the placeholder `func_800C7978` (s1652 observation) — synchronize
only if the full independent comparison agrees.

Competing hypotheses and discriminator:

- H1: the companion mission-overlay name is the live function, and generated
  body, TOML size/name, previous/next boundaries, and section-4 overlay span
  agree completely — synchronize any stale placeholder.
- H2: the name belongs to another overlay or conflicting context — leave the
  generated placeholder and record the collision.
- H3: the name or function evidence is absent, conflicting, or data-like —
  leave unresolved and advance to the next ranked candidate.

Exact commands:

```sh
# 1. Companion mapping / callers / semantics (bounded searches only)
grep -rn 'spawnEffectOnNamedDatItem\|0x800C7978\|800C7978' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 \
  --include='*.c' --include='*.h' --include='*.txt' --include='*.yaml' \
  --include='*.md' --include='*.ld' | grep -v '/build/' | head -80

# 2. Generated definition + adjacent boundaries
grep -rn 'func_800C7978\|spawnEffectOnNamedDatItem\|0x800C7978\|0x800C794C\|0x800C79F0' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --include='*.c' --include='*.h' --include='*.inl' | head -80

# 3. TOML + overlay span
grep -n '800C7978\|spawnEffectOnNamedDatItem' \
  syms/rogue_squadron.syms.toml | head -40
```

Synchronize only on complete independent agreement. No build or runtime run
is required for this work unit. Before starting, re-check the last 15 ledger
titles: if they are all sweep-scoped again, this iteration must be a REVISIT
instead (retail-entry or M4 with a genuinely new angle). s1650 already
consumed the retail-entry revisit for post-B A/Start/Z; do not repeat those
inputs.
