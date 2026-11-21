# NEXT (s7769)
HYPOTHESIS-ID: fps60-l12-half-rate
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers to docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines (expect s7768_fps60_rate_L12). Any of those outranks this.
Fold s7768_fps60_rate_L12: its log ends with `s7768 arm=rN SUMMARY windows=.. slow_windows=.. H-limit=.. H-cost=.. H-other=..`
(re-run `python3 tools/s7768_fps60_rate.py scratch/s7768_soak/log_rN.txt` for detail).
- slow_windows=0 on both arms -> 4/4 non-recurrence since s7749: close item 29 as an unreproduced transient (do NOT queue more repeats).
- H-cost -> the L12 dd4 gfx task crossed 16.7 ms: one run with the s7766/G1E_GRING ring to split RSP ucode time vs RDP/fullsync
  inside send_dl, then fix the dominant term.
- H-limit -> log the guest writer of 0x80128EAF (oracle or a store watch) and extend the FPS60 CAS clamp to that value.
- H-other -> lim=1 and send_dl <13 ms: look at the guest thread cpu (g1b-gt slot 8.3) in the slow windows.
Do NOT add more latency arms, coverage units or crash-hunt soaks.
