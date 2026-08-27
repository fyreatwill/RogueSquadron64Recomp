# NEXT work unit (s2653) — bounded generated-symbol sweep while M5 is blocked

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next bounded symbol region at `0x800CCB1C` using the companion
mission/menu symbols, the generated snapshot, exact spans, callers, and
overlay identity. Rename only a placeholder whose identity is supported by
exact companion and span/caller evidence; unresolved fragments stay
placeholders. Do not change runtime behavior.

## Competing hypotheses and discriminator

- `H-CompanionExact`: a placeholder has an exact companion name and matching
  function span, so a supported rename can be landed.
- `H-BoundaryOnly`: evidence identifies only an adjacent or duplicate boundary;
  retain the placeholder.
- `H-OverlayCollision`: the same VRAM has distinct overlay bodies; retain
  context-specific names and do not collapse them.
- `H-Unproven`: no defensible mapping exists in this region.

The discriminator is one table containing each candidate's address, companion
name/comment, exact overlay span, generated placeholder, callers, and whether
the identity is exact or boundary-only. One exact unresolved row selects a
rename; an already-resolved row advances the cursor; a duplicate VRAM body
selects `H-OverlayCollision`; otherwise the region is `H-Unproven`.

## Exact checks

1. Inspect companion mission/menu symbols, repository TOML, generated body,
   overlay table, and callers around `0x800CC9B8`.
2. Compare adjacent addresses and sizes. If an exact unresolved mapping is
   found, update the repository TOML and run
   `python tools/rename/build_redefs.py` only if an exact supported rename is
   selected, then verify the redef line. Otherwise leave resolved entries
   unchanged.
3. Land at most one companion-supported rename or one tightly bounded exact
   batch; do not invent names from semantics alone.

## Expected outcomes

An exact unresolved mapping lands a regeneration-safe rename and advances the
sweep. An already-resolved mapping, boundary-only result, collision, or
unresolved result records why the placeholder remains and selects the next
bounded region. If an independent generated line is unavailable, record that
limitation and do not claim a two-source result.
