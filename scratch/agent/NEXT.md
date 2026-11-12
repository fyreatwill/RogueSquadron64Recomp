# NEXT (s7214): present-shape census at ASPECT=auto fullscreen (Expand branch of the s7213 fix)
HYPOTHESIS-ID: mode-switch-pillarbox
Context: s7213 fixed the 21:9 mode-switch letterbox flash (first intro/hangar frame squashed into 1360x260) in lib/rt64 present_queue:
when a target's rs.x/rs.y differs >3% from aspectTarget/aspectSource of the present VI, the viewport uses shapeScale {rs.y*want, rs.y}.
Verified at Manual 4:3, 16:9, 21:9 windowed (L17 route, 5+45 s capture). The Expand branch (ROGUESQ_ASPECT=auto: want = max(swapW/swapH,
src)/src) and fullscreen are untested; a wrong `want` there would stretch normal frames.
Hypotheses: H-ok (auto fullscreen: only real mode-switch mismatches log, all viewports full, no box frames); H-false (Expand computes
`want` from swapChain dims that differ from the workload's, so [s7213-shape] fires on ordinary frames and stretches them: fix by using
the same derived ratio the workload queue uses, or compare against sharedResources->resolutionScale of a matching-VI workload).
Discriminator, 2 runs: tools/s7141_arm.zsh 17 <name> "ROGUESQ_G5B_FRAME_EVERY=100000 ROGUESQ_VI_SHAPE_LOG=1 ROGUESQ_ASPECT=auto
ROGUESQ_FULLSCREEN=1" 5 45 with CW/CH = the fullscreen size (one arm), then ROGUESQ_PRESENT_SHAPEFIX=0 (control arm). Count
[s7213-shape] lines (fix=1 vs fix=0 must list the same events), list non-full [g1d-vishape-vp], run
`python3 tools/s7213_box_scan.py <raw> scan` (box frames only in the =0 arm), sheet with scratch/s7213/sheet.py. H-false -> fix and rerun.
Then extend to the long s7210 route (MISSION FAILED -> Elite Rogues) at 21:9 once. Delete raws/caps after scoring.
