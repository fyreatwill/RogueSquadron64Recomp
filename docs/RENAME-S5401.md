# Generated-symbol audit — Session 5401

Candidate: `fake_func_800B89F4`.

## Hypotheses and discriminator

- H1: the short generated record is a callable preamble for `playerVwingInit`.
- H2: it is a data/splat fragment preceding `playerVwingInit`, so no semantic
  function rename is safe.
- H3: the generated and mapping surfaces are already synchronized or the
  address is reused.

The discriminator was the exact generated span compared with the companion
symbol file, the following function boundary, `recomp_overlays.inl`, and the
independent syms table.

## Evidence

- `funcs_31.c` has a record at `0x800B89F4` ending immediately before
  `playerVwingInit` at `0x800B8A00`; its generated body is an explicit
  invalid-C gap filler that traps rather than a callable preamble.
- `rogue_squadron64/symbol_files/mission_overlay.txt` declares
  `fake_func_800B89F4` at `0x800B89F4` and comments that the real function is
  `playerVwingInit`.
- `syms/rogue_squadron.syms.toml` independently assigns
  `data_gap_800B89F4`, size `0xC`, followed by `playerVwingInit` at
  `0x800B8A00`.
- `recomp_overlays.inl` carries the same `0xC`-byte entry and following
  boundary. `tools/rename/build_redefs.py` already maps the fake symbol to
  `data_gap_800B89F4`.

H2 wins. The writer/classification is the companion symbol/splat boundary,
not a game-side callable routine; the bytes are not legitimate function code.
No rename or generated-file change is authorized.
