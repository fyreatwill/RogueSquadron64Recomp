# NEXT: prove s6879/s6880 survive a regen from pristine, then fix the wide + dd arm's missing freeze
HYPOTHESIS-ID: g1d-wide-regen-verify

Why: apply_s6879_fpdepth and apply_s6880_widebound were applied to the live tree only. s6880 runs last in RS64_REPLAY because apply_s6493_stream_cum anchors on the s6049 text. Nobody has replayed that order.
Hypotheses: H-ok (replay applies both, regen_verify shows no new difference) / H-order (an anchor fails, or the s6880 assert 9 == 9 trips) / H-drift (replay passes, but funcs_9 differs from live).
Measure: docs/REGEN-VERIFY.md: tools/regen_front.sh <new dir>, tools/regen_replay.sh <copy of pristine>, tools/regen_verify.sh <that dir> <out dir>. Offline, no game run. Baseline s6864: 75 differ. Control: the live tree's s6880 helper symbol must appear in the regenerated funcs_9 object.
Outcomes: H-ok -> record it. H-order -> fix the step order. H-drift -> name the function and fix the script.
Then: hd4 (16:9 + dd4) and p2/p2s stayed alive with caps=0, so wide + dd has no same-pose frames. Boring-first: check MISSION_WIDTH and the DEBUG_WRITE width those arms actually fly at. If a same-pose wide scorer is wanted at 21:9, g3_aspect_crop.py must first pin sx = sy (s6880: its free fit is invalid there).
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6880_219_depth.png, docs/owner_sheet_s6879_wide_depth.png, docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous, 21:9 lvl5/lvl10 at 300 s. Owner can lift the park for these. lvl10 cloud clock only on an owner report.
