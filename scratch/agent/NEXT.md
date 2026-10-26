# Next: G1d residual is parked; take ladder item 5 (MIPS C-patch qualification) or owner feedback
HYPOTHESIS-ID: cpatch-pipeline-qualification
s6276 closed the s6275 rerun as VOID (frozen frame, no blanking control; see PORTING-STATE s6276). Do not rerun skip-toggle unless the dump reads the RT64 native target or the toggle gates writeback.
Next unit: pick ONE small real C patch (tools/weaken_patched_funcs.py PATCH_WEAKEN target), qualify with the two-arm discipline (patched vs unpatched, same run recipe, positive control that the patch fires), then a 300 s hold. Read docs/CURRENT-TRUTH item 5 first.
