# NEXT work unit (s1652)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. The next candidate is
`func_800C794C`, independently named `getScaledPlayerCraftSpeed` at
`0x800C794C` (size `0x2C`). Generated already uses the human name; TOML still
carries the placeholder `func_800C794C` (s1651 observation) — synchronize
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
rg -n 'getScaledPlayerCraftSpeed|0x800C794C|800C794C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 --glob '!**/build/**' | head -80

# 2. Generated definition + adjacent boundaries
rg -n 'func_800C794C|getScaledPlayerCraftSpeed|0x800C794C|0x800C78A0|0x800C7978' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs -g'*.c' -g'*.h' -g'*.inl' | head -80

# 3. TOML + overlay span
rg -n '800C794C|getScaledPlayerCraftSpeed' \
  syms/rogue_squadron.syms.toml | head -40
```

Synchronize only on complete independent agreement. No build or runtime run
is required for this work unit. Before starting, re-check the last 15 ledger
titles: if they are all sweep-scoped again, this iteration must be a REVISIT
instead (retail-entry or M4 with a genuinely new angle). s1650 already
consumed the retail-entry revisit for post-B A/Start/Z; do not repeat those
inputs.
