# NEXT (s7972)
HYPOTHESIS-ID: post-preset-class-ladder
s7971 closed class MP (host memory pressure, real 5 GB hog; game pages compressed 55 MB, presents 59-60/s, 0 underruns): H-moot,
no code change, gate S7971_MP. Do not redo MP, SW, UE, XF, CS, DI, RO, AN, PS, SD, DR, RD, FW, CK, LC, TF, EV.
Note: CURRENT-TRUTH is 59 KB, near the 60 KB maintenance trigger; if Step 0 prints > 60000, do maintenance instead.
Trap from s7971: present-ring Q rows are host-uptime stamped, ROGUESQ_AI_TRACE rows launch-relative; align with
tools/s7971_mp_score.py align() before windowing on a launch offset.

## Work unit: ladder 3c host class NS (data volume full while the game runs: the NON-save writers)
s7357 covered the save path on a full disk (EEPROM main/.bak). Not covered: every other writer that runs during normal play when the
data root's volume is full: RT64 shader/pipeline cache, settings.txt writes from the F1/F6 panels, controls.json save (F6), log files,
rs64 crash breadcrumbs, the s7969 relocated exe copy in ~/Library/Caches (only when off-volume). Proxy without filling the owner's
disk: a small APFS disk image (`hdiutil create -size 200m -fs APFS`, attach, no sudo), private game copy + COPIED save inside it,
fill it with a filler file to 0 bytes free (`mkfile`/dd until ENOSPC) at a phase-gated point, then exercise the writers.
Hypotheses:
- H-crash: a writer treats a failed write/close as impossible (unchecked fwrite/fclose, std::ofstream without checks) -> abort/crash.
- H-silent: a writer truncates then fails -> an empty/partial controls.json or settings.txt that the next launch reads as defaults
  (owner loses bindings/settings silently). Outcome: file size 0 / truncated after the run, next launch logs defaults.
- H-stall: a writer retries in a loop on the game or render thread -> VI holds / present gaps (score like s7971).
- H-moot: every writer fails cleanly, files keep their previous content, 0 crash, presents 60/s.
Positive control: same run, the image NOT full (writers succeed, files change) and a planted truncate (old non-atomic write path, if
one exists, via a mutant env) showing the silent loss is detectable by the scorer.

## Commands (one game at a time)
0. `python3 tools/crash_reports.py --since 2026-11-26`; fold any new SOAK-RESULTS lines.
1. Census first (offline): grep every fopen("w"/"wb")/ofstream/std::filesystem write in src/, lib/rt64/src (outside contrib),
   lib/N64ModernRuntime; classify each as atomic (temp+rename, checked) or truncate-in-place; s7958_fw's census is the starting list.
2. tools/s7972_ns_e2e.zsh: arms not-full control / full-at-title / full-in-flight; drive the F6 save + a settings write via existing
   in-flight toggle hooks (tools/s7764_inflight_toggles.zsh) if possible, else the s7765 controls dump path.
3. Fix only what is ours; gate tools/s7972_ns_gate.py, add S7972_NS to s7651 ARGS + EXTRA_GATES, review rows for any new
   thread/loop/atomic/env, then the full sweep (--jobs 2) after the last game run.
