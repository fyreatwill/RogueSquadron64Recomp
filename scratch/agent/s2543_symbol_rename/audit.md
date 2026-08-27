# Session 2543 symbol-rename audit

The required preflight found that the last 15 ledger titles were not all
sweep sessions, so the generated-symbol sweep remained eligible. The complete
active span at `0x800AD378` is eight bytes:

| address | generated instruction | result |
|---|---|---|
| `0x800AD378` | `sw t1, 0x4(v0)` | renamed |
| `0x800AD37C` | `sw t2, 0x8(v0)` | renamed |

The companion symbol input had only `fake_func_800AD378`; it had no exact
human name, m2c definition, or caller attribution. The neighboring function
starts at `0x800AD380` and is independently named
`computeTrackedObjectWorldAnchor`. The complete body is a callable two-word
field store, so the bounded semantic name
`storeTrackedObjectAuxiliaryFields` describes both writes without absorbing
the neighboring function.

The regeneration-safe rename was added to `tools/rename/build_redefs.py`,
then synchronized into the active companion symbol input and generated
declaration, implementation, and overlay table. No runtime behavior or
mitigation was changed.

Selected: `H-named-match` at semantic-confidence scope. The exact companion
decomp name remains unavailable; this is a bounded local-semantic rename,
not a claim about a higher-level game API.
