# NEXT: s6631 level-select tear re-check at 21:9 (heapslot + s6690 cull mask fix), then G3d
HYPOTHESIS-ID: g1d-levelselect-recheck
s6690 closed the 21:9 hangar SIGBUS (spike cull 8 MB mask folded the 12 MB RDP buffer onto overlay code).
Two landed changes since the s6631 tear fix touch wide-aspect memory: s6689 heapslot (retail gap==0
heap branch when wider than 4:3) and s6690 kSubmitRamMask. Re-run the s6631 level-select tear check
(recipe/evidence: docs/CURRENT-TRUTH "G1d 21:9 level-select tear", scratch/agent/s6631_heapcap_at/).
Hypotheses: H-clean (both fixes compose: no tear, no crash) vs H-regress (heapslot moves the heap so
the s6631 punch no longer caps the arena -> tear/crash returns). Discriminator: the s6631 scorer on
21:9 level select + a 21:9 lvl1 flight framebuffer (game FB dump, not screencapture: window PNGs are
white) showing the extra width drawn. Then G3d turning-shake (ITERATION 3c).
