# Session 2602 symbol census: `0x800E406C`

## Static discriminator

| Check | Result |
|---|---|
| Generated entry | `fake_func_800E406C` in `RecompiledFuncs/funcs_39.c` |
| Instruction span | One instruction: `sw $a0, 0x20($sp)` |
| Previous body | `playDualTextureAttachmentCueMode1` ends at `0x800E4068` |
| Next body | `handleRayShieldedNpcDestroy` starts at `0x800E4070` |
| Companion symbol | `fake_func_800E406C` only; no semantic alias or duplicate-deletion note |
| Exact-address source/m2c/caller search | No match outside the generated/symbol entries |
| Generator check | `python3 tools/rename/build_redefs.py` succeeded; no mapping added |

## Hypothesis result

`H-BoundaryOnly` selected. The entry is an isolated boundary fragment between
two complete functions, and the companion project supplies no defensible human
name. The placeholder remains unchanged. No runtime build or game run was
performed.
