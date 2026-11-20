# NEXT (s7679)
HYPOTHESIS-ID: g6c-standin-attract-cine

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7678 found a deterministic, no-input route that loads real levels (attract demo playlist: L0 -> L5 -> L7 -> L10 in 420 s,
identical bk_calls across runs) and proved the stand-in rebuild/re-key on it. The same run shows stand-ins ACTIVE during the
attract flybys (107 [standins-spawn] lines). The flybys are scripted camera shots, and the owner sees them at the title screen.
Question: do stand-ins put objects into attract/cinematic shots where retail shows nothing (H-cine-ghost), or only bridge objects
the shot later spawns anyway (H-cine-ok)? And do any appear inside the retail dd1 radius (should be none)?
Measure, ONE run: scratch/s7678/run.zsh with ROGUESQ_STANDINS=tog (whole-second on/off windows, same run) plus framebuffer
captures (CAP0 ~20, the s7630 contact-sheet tooling / ROGUESQ_STANDINS_DUMP a:b:n windows); score per shot the clustered diff px
between on and off seconds (tools/s7630-era scorer, `--cluster 16`), and list [standins-spawn] early_s per level: a stand-in with no
matching spawn before the level changes (spawn line absent for its item) = an object the cinematic never shows = H-cine-ghost.
Positive control: the same scorer must show the known L0 bridged spawns (fix arm: 88 item handoffs) as on/off diffs.
If H-cine-ghost: gate stand-ins off in attract/cutscene views (find the attract/demo flag; s6911 [ddscene] attribution names the
scene), default stays STANDINS off anyway. If H-cine-ok: note it for the owner sheet and take the next G-rung.
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, no repeat-hold soaks.
