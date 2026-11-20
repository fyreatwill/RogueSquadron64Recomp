# NEXT (s7696)
HYPOTHESIS-ID: post-g6c-owner-wait-s7696

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
State: G6c owner-judged (s7691 sheet); s7692-s7695 re-gates on the post-G6c binary all clean (holds, UB gates/censuses, G5c freezes,
G2b crawl audio + G5d logo: tools/s7695_cine_audio_gate.zsh, crawl ctl 1037 vs fix 2, logo 0.092 on/off).
Step 0: CURRENT-TRUTH ~58.6 KB; if > 60000, maintenance (migrate s7660-s7692 G6c detail in Next steps item 20 to PROJECT-OVERVIEW).
Otherwise the first open rung not waiting on the owner. Candidate: G5h cutscene background re-check at dd4 with STANDINS=1 (do stand-ins
appear in mission intro/outro cutscenes, and do they look right there? the s7695 gate showed they do not run in the boot cinematic, but
mission cutscenes run inside the level). Hypotheses: H-absent (cutscene path does not reach runInMissionFrame 0x800FAC68), H-drawn-ok,
H-drawn-wrong (stand-ins at the wrong place for the cutscene camera). Discriminator: STANDINS=tog on a forced-level intro cutscene
(s6908-s6919 recipes), [standins-s] added>0 during the cutscene + same-run on/off frame pairs.
zsh note: never store `$!` in an associative array (s7695: stored literally); use scalars.
