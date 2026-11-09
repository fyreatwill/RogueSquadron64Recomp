# NEXT: dd6 bundle per-level sweep, second batch: L0, L8, L9, L11, L12 at 16:9
HYPOTHESIS-ID: dd6-bundle-level-sweep
Context: s7041 held L2, L3, L6, L7 clean (~505 s each, cull fires, fps 59.1-60.0). Unrun at the dd6 bundle: L0, L8, L9, L11-L18 (L10 cloud level: health only).
Unit (one game at a time, ~10 min per level; check the screen is unlocked first, the tool does):
  env LEVELS="0 8 9 11 12" TAG=S42 zsh tools/dd6_bundle_level_sweep.zsh scratch/s7042 > scratch/s7042/sweep_report.txt 2>&1
  (mkdir -p scratch/s7042 first; ANALYZE_ONLY=1 re-scores without running.)
Per level read: alive_at_end, vi_stalls30s, crashlines, fps/rsp per phase, ocull/f per phase.
Outcomes: H-clean (all hold, bundle phases >= off phase fps) -> extend the OWNER-OPT-INS level list, then L13-L18 next;
H-fail (crash/stall/fps drop on a level) -> root-cause that level (backtrace, writer), it is a datum; H-nocull (ocull 0 on a level) -> note it, bundle harmless there.
