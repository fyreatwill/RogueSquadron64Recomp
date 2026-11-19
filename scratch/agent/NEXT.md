# NEXT (s7670)
HYPOTHESIS-ID: f6-panel-resize

s7669 closed rumble across abort/hangar (clean, control PASS; scratch/s7669). First: `python3 tools/crash_reports.py --since 2026-11-13`
(a NEW report outranks everything). Otherwise an owner report; else the F6 panel at a live window resize:
ROGUESQ_WIN_TEST_RESIZE_S to a 21:9-class size (1512x648) with ROGUESQ_ASPECT=auto, panel opened by ROGUESQ_PANEL_TEST_WINDOW.
Hypotheses: H-ok (`[controls-panel] stale` fires once, draws resume at the new fb size within 0.5 s), H-squash (panel drawn at the
old size after the resize, like the s7668 toggle case), H-crash (Metal drawable size mismatch). Discriminator: per-draw panel
size vs fb size log across the resize; same-run control arm without the panel. tools/g1e_owner_quiet_arms.zsh arms, one game at a time.
Do NOT do census-gate housekeeping or repeat-hold soaks (G4 parked). Never touch build/saves; SIGKILL only; <=2 CPU-heavy jobs.
