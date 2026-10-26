# Next: G3c(b) knife spikes - vertex-level replay of a logged wedge
HYPOTHESIS-ID: g3c-owner-visual
s6300 exonerated the divide unit (VRCP/VRSQ tables match hardware ROM). Remaining: H-rsp-emu in clip/multiply ops (VCH/VCL/VCR/VMULF/VMACF/VMUDN family in rsp_vu_impl.hpp) vs H-retail (hardware yields the same pinned Y -170.25/-224.25).
Unit: add ROGUESQ_LOG_SPIKE-gated dump of the DMEM vertex block + matrix for the first flagged swap (one build), run lvl2 flight 120s, then recompute that vertex's clip/projection offline in python per docs/F5-UCODE-REFERENCE.md. Positive control: a non-flagged vertex from the same DL must reproduce its logged RDP coords exactly. Outcome A: recompute == RDP output -> ucode math faithful, ask owner about CULL_SPIKE default. Outcome B: differs -> bisect to the op.
Then G3c(c) shake (jerk measurement), G3c(a) vertex probe.
