# 0x800AE3E4 classification

## Candidate

| Field | Evidence |
|---|---|
| Project symbol | `fake_func_800AE3E4`, mission overlay, VRAM `0x800AE3E4`, size `0xC` |
| Generated location | `RecompiledFuncs/funcs_28.c`, declaration in `funcs.h`, mission registration in `recomp_overlays.inl` |
| Generated body | Three instructions: `lwc1 $f0,0x58($fp)`, `lwc1 $f2,0xC4($fp)`, `mul.s $f0,$f0,$f2`; no prologue, return, or complete host-level result path |
| Predecessor | `isCameraTransitionIdle` starts at `0x800AE3BC` and ends at `0x800AE3E4` |
| Successor | `initPlayerCraftTrailBuffers` starts at `0x800AE3F0`; the candidate's final word at `0x800AE3EC` overlaps the menu overlay's `tickEasedCameraKeyframeBlend` entry |
| Companion maps | Mission map retains `fake_func_800AE3E4`; menu map names `tickEasedCameraKeyframeBlend` at `0x800AE3EC`; no exact semantic name is supplied for the candidate |
| Callers/lookups | No generated call or independent absolute lookup for `fake_func_800AE3E4` was found; only its declaration, definition, and overlay registration occur |

## Competing hypotheses

- H-Callable: rejected. There is no callable entry contract, return, caller, or exact semantic companion name.
- H-DataGap: rejected. The bytes decode as a real three-instruction executable fragment, not a mechanically bounded non-code gap.
- H-Fragment: selected. The record is an overlay-boundary/internal executable fragment, with an overlapping entry in the companion menu overlay and no independent callable evidence.

## Disposition

Retain `fake_func_800AE3E4` in all generated and source maps. No rename or
build is justified. This is static, single-source classification; it does not
establish runtime reachability.
