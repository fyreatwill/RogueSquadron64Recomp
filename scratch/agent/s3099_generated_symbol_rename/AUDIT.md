# Session 3099 generated-symbol audit: `0x80072CE8`

| Surface | Evidence | Result |
| --- | --- | --- |
| Companion map | `rogue_squadron64/symbol_files/main_overlay.txt` names `initWaterSprayParticlesPreamble` at `0x80072CE8` and describes it as the defined two-instruction entry fragment for `initWaterSprayParticles` at `0x80072CF0`. | Exact identity |
| Generated body | `N64Recomp/RecompiledFuncs/funcs_18.c` contains the two instructions `addiu $v1,$v1,-0x4160` and `addu $v0,$v1,$v0`, already under `initWaterSprayParticlesPreamble`; the complete callable body begins at `0x80072CF0`. | Preamble fragment |
| Callers | Exact search of active generated `.c`/`.h`/`.inl` files found only the definition, declaration, and overlay registration for the preamble; no standalone generated caller or independent lookup exists. | No standalone caller |
| Header | `N64Recomp/RecompiledFuncs/funcs.h` declares `initWaterSprayParticlesPreamble`. | Synchronized |
| Overlay registration | `N64Recomp/RecompiledFuncs/recomp_overlays.inl` registers the 8-byte span at ROM offset `0x000728A8` as `initWaterSprayParticlesPreamble`. | Synchronized |
| Project TOML | `syms/rogue_squadron.syms.toml` was the only stale active surface and now uses `initWaterSprayParticlesPreamble`. | Synchronized |

The companion identity and the generated body/header/registration independently
agree on a preamble fragment belonging to `initWaterSprayParticles`; this
selects H-ExactIdentity. No runtime, audio, route, or mitigation behavior
changed.

## Checks

- No remaining `fake_func_80072CE8` reference exists in the project TOML or
  active generated tree.
- The next unresolved project placeholder is `fake_func_800AE3E4`.
