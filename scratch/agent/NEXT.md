# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e per-level game fps at 21:9 in deep flight (s6990 closed 16:9: 60.0 on all 19 levels)
HYPOTHESIS-ID: g1e-game-fps
Why: the owner plays on a 21:9 ultrawide; s6962 lvl1 21:9 had p10 52 and a present level; s6990's 16:9 window (t 95-150) may
include intro cutscenes. Hypotheses:
- H-60w: all levels hold ~60 tasks/s and shown/s at 21:9 deep in flight -> G1e frame rate closed for both owner screens.
- H-wide-drop: some levels drop below ~55 at 21:9 (wider terrain footprint) -> name them, split cost with [g1b] sd_wall / g1e_sync_rate.py.
- H-dup: shown/s < gen/s or rep% > 0 -> present pacing bug.
Unit: edit scratch/s6990/drive.sh into scratch/s6991/drive.sh: R=scratch/s6991q, add ROGUESQ_ASPECT=21:9 to X, HOLD=240, keep C30.
Score: python3 tools/g1e_level_fps.py scratch/s6991q C30 L0 ... L18 --from 150 (flight keys from t=95, initMission t~67).
Positive control: C30 must read 30.0. Check the host is idle (HID idle > 120 s) first; the harness exits 2 on human input.
