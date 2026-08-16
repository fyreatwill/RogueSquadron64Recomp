# NEXT work unit (s1658)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the exact generated-symbol census. The next candidate is companion
`despawnEffectOnNamedDatItem` at `0x800C7C88` (size `0x64`). Generated and
overlays already use the human name; TOML still carries `func_800C7C88`
(s1657 observation) — confirm full independent agreement and correct the
stale TOML name if the body/boundaries agree, or leave unresolved and
advance.

Competing hypotheses and discriminator:

- H1: the companion mission-overlay name is the live function, and generated
  body, TOML size/name, previous/next boundaries, and section-4 overlay span
  agree completely — synchronize any stale placeholder (TOML name).
- H2: the name belongs to another overlay or conflicting context — leave the
  generated placeholder and record the collision.
- H3: the name or function evidence is absent, conflicting, or data-like —
  leave unresolved and advance to the next ranked candidate.

Exact commands:

```sh
# 1. Companion mapping / callers / semantics (bounded searches only)
grep -rn 'despawnEffectOnNamedDatItem\|0x800C7C88\|800C7C88' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 \
  --include='*.c' --include='*.h' --include='*.txt' --include='*.yaml' \
  --include='*.md' --include='*.ld' | grep -v '/build/' | head -80

# 2. Generated definition + adjacent boundaries
grep -rn 'despawnEffectOnNamedDatItem\|func_800C7C88\|0x800C7C88\|0x800C7C28\|0x800C7CEC' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --include='*.c' --include='*.h' --include='*.inl' | head -80

# 3. TOML + overlay span
grep -n '800C7C88\|despawnEffectOnNamedDatItem\|func_800C7C88' \
  syms/rogue_squadron.syms.toml | head -40
```

Synchronize only on complete independent agreement. No build or runtime run
is required for this work unit. Before starting, re-check the last 15 ledger
titles: if they are all sweep-scoped again, this iteration must be a REVISIT
instead (retail-entry or M4 with a genuinely new angle). s1650 remains the
only non-sweep title in the last-15 window through s1664; s1665 will force
the mandatory revisit if the intervening sessions stay sweep-scoped. Do not
repeat already-tested retail-entry inputs (hold/A/B/Z, valid D-pad,
post-viewer C/L/R, post-B A/Start/Z).
