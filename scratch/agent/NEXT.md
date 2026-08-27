# NEXT work unit (s2661) — continue generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Audit the next bounded group of address-coded generated symbols after the
audio-resampling batch. Use only exact companion symbol entries plus matching
generated/TOML spans; preserve overlay-qualified names and do not infer names
from address boundaries alone. Land the next exact batch in
`syms/rogue_squadron.syms.toml` and, when needed, refresh the rename mapping.

## Competing hypotheses and discriminator

- `H-CompanionExact`: the companion symbol file supplies an exact semantic or
  overlay-qualified identity with a matching generated span.
- `H-OverlayCollision`: the address is occupied by distinct overlay identities
  and must remain context-qualified rather than collapsed.
- `H-Unresolved`: no independent companion identity or exact span exists.

The discriminator is one table keyed by VRAM address with companion name,
overlay, generated definition, size/end boundary, TOML identity, and caller
evidence. Only `H-CompanionExact` rows are renamed; collision and unresolved
rows remain unchanged.

## Exact commands

1. Inspect the next address-coded region in the companion symbol files and the
   checked-in TOML; use `rg` and bounded `sed` windows only.
2. Apply one bounded rename batch with `apply_patch`.
3. Verify TOML rows and run the repository rename-map check if its sibling
   companion checkout is available. Do not build or run the game for a symbol
   map-only change.
4. Record the table and selected hypothesis in the next ledger entry.

## Expected outcomes

- Exact companion/span rows select `H-CompanionExact` and land a rename batch.
- Distinct overlay occupants select `H-OverlayCollision` and leave names
  context-qualified.
- Missing evidence selects `H-Unresolved`; choose a later address window and
  do not invent a semantic name.
