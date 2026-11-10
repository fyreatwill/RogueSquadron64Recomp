# NEXT: dd6 bundle per-level sweep, third batch: L13-L18 at 16:9
HYPOTHESIS-ID: dd6-bundle-level-sweep
Context: s7041/s7042 held L0, L2, L3, L6-L9, L11, L12 clean (~505 s each, cull fires, bundle 59.6-60.0 fps). L12 needs the cull (off phase 42.8 fps, P(>=2VI) 0.40).
Unrun at the dd6 bundle: L13-L18 (L10 cloud level: health only). Six levels ~60 min; one game at a time.
Unit: mkdir -p scratch/s7043; env LEVELS="13 14 15 16 17 18" TAG=S43 zsh tools/dd6_bundle_level_sweep.zsh scratch/s7043 > scratch/s7043/sweep_report.txt 2>&1
(run in background; ANALYZE_ONLY=1 re-scores without running). Note L7/L16/L17 autopilot holds may cycle the backdrop menu (G1e item 11): check flight_s.
Per level read: alive_at_end, vi_stalls30s, crashlines, fps/rsp per phase, ocull/f per phase.
Outcomes: H-clean (all hold, bundle phases >= off phase fps within 0.4 A/A) -> close the sweep, OWNER-OPT-INS says all levels;
H-fail (crash/stall/bundle fps < 59 on a level) -> root-cause that level (backtrace, writer), a datum; H-nocull (ocull 0) -> note, bundle harmless there.
