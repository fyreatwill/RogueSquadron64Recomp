Single next work unit (s5595): fold s5594_hangar_long_k and _l (loop runs them; do NOT run the game).
Commands: grep -n "s5594" scratch/agent/SOAK-RESULTS.md ; grep -h '^tag=' the logs (vi_stalls30s, crashlines).
Outcomes: any CRASH/stall -> lldb attach backtrace, name writer, root-cause fix. Clean -> M6 first-mission fully closed; pivot to ASan arm or second-mission route (flag 0x130B58 bit 0x02000000 never set on title->mission route, see s5515).
HYPOTHESIS-ID: m6-mission-endurance
