# NEXT: G1c phase 2 — explain HUD-absent frames at dd3/dd4 and the 420 s survival
HYPOTHESIS-ID: g1c-dd-phase2
s6407: dd3/dd4 (needs ROGUESQ_DD_UNSAFE=1) hold 183 s clean but lose HUD on ~5% of frames with 0 ucode-cap fires. Read SOAK-RESULTS for s6408_dd34_long (420 s u3/u4). If they survive 420 s: pose-lock phase-gated comparison of HUD-absent frames (log DL chunk count/last-chunk per frame, ROGUESQ_DLPOOLLOG) to name the truncation writer; if they die: backtrace via lldb, finder-null = chunk pool (s6280). Positive control: retail+UCODE_CAP=1500 drops craft/HUD. Defaults unchanged.
