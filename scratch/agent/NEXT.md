# NEXT (s7838)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Fold s7837_vistamp_L1 if it ran: rV (VI_STAMP=1) and rC must both be alive, with vi_stalls30s=0, and rV max_gap /
slow windows no worse than rC. The vistamp_on echo must read rV=1 rC=0 (this is the positive control). If it passes, add
VI_STAMP=1 to CURRENT-TRUTH "Owner decisions pending" as a determinism-only candidate default. If it fails, root-cause it before
anything else. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: s7837 closed port determinism. The sub-VI host jitter forks identical runs (H-jitter), and ROGUESQ_VI_STAMP=1 removes it.
The whole-VI onset count still varies with load time (inherent, H-guest). The G3 flight det sweep resumes: lvl2 and lvl3 are closed
as H-dtpath. Next is mission 4 (Liberation of Gerrard V, save byte 0x31=3), with VI_STAMP=1 in the port arm so the port path is
VI-exact like retail's.
Unit (s7836 recipe on level 4):
  save: `python3 tools/g3_eep_patch.py scratch/s6748/lvl2.eep scratch/s7838/lvl.eep --set 0x31=3`
  port: `env SAVE_FROM=scratch/s7838/lvl.eep SECS=150 CAP0=140 AP=<s7836 AP> XE="ROGUESQ_AUTOPILOT_CLOCK=vi ROGUESQ_S7834_RAMDUMP=1
        ROGUESQ_G3C_CAMLOG=1 ROGUESQ_S7835_DT=1 ROGUESQ_VI_STAMP=1" zsh tools/g3_port_capture.sh scratch/s7838/p1`
  retail R1/R2: the s7836 retail recipe (tools/s7828_retail_cpo.sh, CPO 2, R1 OFF 5.75, R2 OFF 4.25, plus r1d --pc-ram-dump) with
  the new save. Score: s7827 tri census --controls, tools/s7836_hud_elem_census.py, ramdump via scratch/s7837/q.py alignment
  (skip truncated rows).
Outcomes: H-exact (tri mode 0, HUD exact, RAM equal past onset) / H-dtpath (forks at an onset whole-VI dt, render exact) /
H-defect (missing class, or world-tri shift beyond retail-vs-retail). Note that Gerrard V is the G5a mission; log any actor anomaly.
