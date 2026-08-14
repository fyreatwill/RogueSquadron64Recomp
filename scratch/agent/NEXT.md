# NEXT work unit (s1008)

s1007 (Buffy, offline): every zero-shade `[shade-raw]` row carries the fixed
decoded shade base (-32768,-32768,-32768,+32768) = `0xFFFF8000` RGB /
`0x00008000` alpha — a constant -0.5/+0.5 sentinel — while the same task's
op=0x02 vertex-color payload is nonzero and correct. The source-to-consumer
join is therefore closed; the divergence is in the ucode's shade emission.
A `slotDispatcherIter` sp-guard instrument (`ROGUESQ_LOG_SLOT_SP_GUARD=1`) is
landed and build-verified; a soak is queued.

HYPOTHESIS-ID: m4-zero-shade-emission-constant

## One work unit

Trace the recompiled Factor 5 ucode's shaded-triangle shade emission against
the GLideN64 reference (`reference/gliden64/F5Rogue.cpp`,
`F3DSWRS_VertexColor` / `F3DSWRS_PrepareVertices`), which copies unsigned u8
RGBA per vertex with no lighting and no -0.5 sentinel. Do not add a mitigation
or hand-edit generated files. Static audit only — no build/run required.

Competing hypotheses and discriminating measurement:

- `H-signed-color-load`: the ucode (or its RSPRecomp) sign-extends the color
  byte (lb vs lbu), and the -0.5 sentinel is the sign-extended/zero color path.
- `H-shade-source-mismatch`: the ucode emits shade from a light/normal register
  that is uninitialized (-0.5) instead of the fetched color array.
- `H-emission-layout`: the ucode writes the shade words to the wrong DP ring
  offsets, so RT64 reads a constant.

Discriminator: locate the generated ucode's color-fetch and shade-word store
sites (RSP_MEM_*_LOAD sites touching the vertex-color array; RSP_MEM_*_STORE /
DP-ring writes that produce the triangle shade words) and compare their width,
signedness, and register source against F5Rogue.cpp. A signed load feeding the
shade store selects `H-signed-color-load`; a store sourced from a non-color
register selects `H-shade-source-mismatch`; correct sources with mismatched
offsets selects `H-emission-layout`.

## Head-start already located (do not start from zero)

All line numbers are `build/factor5_ucode/factor5_ucode_recompiled.c`. Verify
these leads against the embedded disassembly comments; no build/run needed.

- **Color fetch (correct, `lbu`)**: lines 830-854 load the 4 RGBA bytes with
  `lbu` (unsigned) into the DMEM vertex-color table (0xB70-0xB73) — matches
  F5Rogue.cpp `F3DSWRS_PrepareVertices`. Not the bug.
- **Sign-extension suspect**: line 1692 `lb $10, 0x37($18)` is the ONLY signed
  byte load in the emission path, sitting right before `lbu $2, 0x3A($18)`
  (line 1706) — the exact `lb`-vs-`lbu` asymmetry behind `0x8A -> 0xFF8A =
  -118`. Trace what writes DMEM 0x137 (state base 0x100 + 0x37): if it is a
  color byte, `lb -> lbu` is the fix for `H-signed-color-load`.
- **Shade-word store site**: lines 1770-1839 store the 8 shade halfwords via
  `SSV` at `0x8($16) .. 0x1E($16)` — these are the `[shade-raw]` baseFixed
  words. They multiply by `$v30[4]`/`$v31[4]` (the 0.5-in-1.16 constants), so
  the constant -0.5/+0.5 sentinel comes from a zero color input to that
  multiply.
- **Sentinel root-cause candidate**: the ±0.5 constant means the color fetched
  in §color-fetch never reaches the multiply. Trace whether the DMEM 0xB70-
  0xB73 table is consumed between lines 854 and 1690. If not, that gap selects
  `H-shade-source-mismatch` (emission reads an uninitialized register).
