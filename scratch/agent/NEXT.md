# NEXT: G3c(a) H-grid — find the real terrain Vtx position writer
HYPOTHESIS-ID: g3c-owner-visual

s6361: no `sh` Vtx position store exists in 0x8004A6C0/0x8004B644/0x8004B938 (static, single-source). Per-cell 100-byte records at *(0x80137A50)+idx*100 (cell+0x48 holds the pointer); float positions at *(0x80137A54)+idx*12.
Work unit: grep funcs_*.c for consumers of cell+0x48 / the 0x80137A50 records (lh/lhu/sh with idx*100 or 0x64 stride, and the F5 VTX DMA source), identify the Vtx y store, add opt-in ROGUESQ_EDGE_FADE_R2_Y (y lerp toward horizon over r=26..34, fixup-backed) plus a +50 y control arm, soak nofade/y/yred with the s6359 recipe, score with tools/g3c_horizon_score.py.
- jump_med drops >0.03 -> adopt, bundle into DRAW_DISTANCE, ask owner.
- control visible but jump unchanged -> raise footprint radius past 34.
- control invisible -> hook not on drawn cells; fix before concluding.
