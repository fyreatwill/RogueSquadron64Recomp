# NEXT work unit (s2624) — bounded generated-symbol sweep while M5 is blocked

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit one bounded symbol region centered on `0x800C63C0` and its neighboring
`0x800C64A4/0x800C64B0` entries using companion symbols, generated bodies,
callers, and overlay sizes. Rename only a symbol whose identity is supported by exact
companion and span/caller evidence; unresolved fragments stay placeholders.
Do not change runtime behavior.

## Competing hypotheses and discriminator

- `H-CompanionExact`: one placeholder has an exact companion name and matching
  function span, so a supported rename can be landed.
- `H-BoundaryOnly`: evidence identifies only an adjacent or duplicate boundary;
  retain the placeholder.
- `H-Unproven`: no defensible mapping exists in this region.

The discriminator is one table containing each candidate's address, companion
name/comment, exact overlay span, generated placeholder, callers, and whether
the identity is exact or boundary-only. One exact row selects a rename.

## Exact checks

1. Inspect `syms/rogue_squadron.syms.toml`, companion
   `symbol_files/mission_overlay.txt`, and the generated symbol/body around
   `0x800C41B0`; use `rg` and bounded `sed` windows.
2. Compare adjacent addresses and sizes and enumerate generated callers. Run
   `python tools/rename/build_redefs.py` only if an exact supported rename is
   selected, then verify the resulting redef line.
3. Land at most one companion-supported rename; do not invent names from
   semantics alone.

## Expected outcomes

An exact mapping lands a regeneration-safe rename and advances the sweep. A
boundary-only or unresolved result records why the placeholder remains and
selects the next bounded region. Do not return to the blocked M5 null
experiment.
