# Generated-symbol audit: `func_800E9AE0`

The bounded exact-span test was applied to the remaining mission-overlay
placeholder.

- The generated body in `../N64Recomp/RecompiledFuncs/funcs_39.c` is a real
  callable function from `0x800E9AE0` through `0x800E9BF0`, with a `0x114`
  byte span and a normal prologue/epilogue. The next generated function,
  `playStateGatedDestroySound`, begins at `0x800E9BF4`.
- `recomp_overlays.inl` and `funcs.h` agree on that exact span and the
  address-coded generated name.
- The companion mission-overlay map explicitly preserves `func_800E9AE0`
  because a false `func_800E9B10` reference makes the surrounding region
  appear split. It provides no semantic name for this body.
- The independent syms table gives the span the address-coded name
  `func_mission_overlay_800E9AE0`, not a semantic function name.
- No generated caller or independent semantic mapping was found.

Decision: H2. The exact callable span is established, but the available
maps classify it as an address-coded overlay placeholder with a documented
false split. A semantic rename is not safe, so no generated or mapping file
was changed.

The generated-symbol sweep has no remaining supported rename candidate. The
next work unit should be a genuinely new discriminator for the parked
retail-entry or M4 boundary thread, not another name census.
