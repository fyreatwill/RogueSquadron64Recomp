# NEXT work unit (s1651)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. The next candidate is
`func_800C78A0`, independently named `calculateDatItemDistanceToPlayer` at
`0x800C78A0` (size `0xAC`).

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
rg -n 'calculateDatItemDistanceToPlayer|0x800C78A0|800C78A0' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 --glob '!**/build/**' | head -80

# 2. Generated definition + adjacent boundaries
rg -n 'func_800C78A0|calculateDatItemDistanceToPlayer|0x800C78A0|0x800C7884|0x800C794C' \
  RecompiledFuncs -g'*.c' -g'*.h' -g'*.inl' | head -80

# 3. TOML + overlay span
rg -n '800C78A0|calculateDatItemDistanceToPlayer' \
  us.rev1.toml overlays.json syms 2>/dev/null | head -40
```

Synchronize only on complete independent agreement. No build or runtime run
is required for this work unit. Before starting, re-check the last 15 ledger
titles: if they are all sweep-scoped again, this iteration must be a REVISIT
instead (retail-entry or M4 with a genuinely new angle). s1650 already
consumed the retail-entry revisit for post-B A/Start/Z; do not repeat those
inputs.
