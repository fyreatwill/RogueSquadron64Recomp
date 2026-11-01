# NEXT: close G1c phase 2 (owner sheet), then G3 render fidelity
HYPOTHESIS-ID: g1c-phase2-closure

s6702: the lvl1 dd8 crash (s6701 soak, 219 s) was the s6569 malloc spill arena LEAKING: rs_free ignored spill pointers,
the 4 MB bump filled, rs_malloc returned NULL, instantiateNamedMeshInstance dereferenced NULL+0xA. Spill now has a coalescing
free list (src/main/upstream_compat.cpp rs64_s6569_isspill releases; ROGUESQ_SPILL_LEAK=1 = old leak). FPS60 dd4 lvl5 = ~44-45
tasks/s past the start pause (not affordable at 60).
1. Fold the queued s6702_spillleak_ctl_dd8_lvl1 soak (SOAK-RESULTS): it MUST show "arena full" (positive control for the fix).
   If it does not, the leak needs longer than 300 s to bite on that run; compare spill bump growth rate instead
   (grep -a '\[spill\]' run.log | tail -1, used 0x... vs t).
2. Owner sheet: lvl1 + lvl5 dd1 / dd4 / dd8 late flight frames (tools/contact_sheet.py), update docs/DRAW-DISTANCE.md (dd>4 adds
   no terrain on lvl1/lvl5; dd8 needs the s6701 pnorm cap and the s6702 spill free list). Close G1c phase 2, defaults unchanged.
3. Next rung: G3 render fidelity (hangar artifacts list in CURRENT-TRUTH, flight vs retail frames).
