# NEXT: fold s6580 true-dd4 lvl10/lvl1 soaks (queued)
HYPOTHESIS-ID: g1c-dd-phase2
s6579: lvl5 true dd4 (multiplier 4 confirmed in log) 301 s hold, 0 stall, 0 crashlines. lvl10 "allattempts-failed" = harness false-nomission (flight origins 0x6A2900/0x644D00, MISSION_RE default 690400; 0 CRASH in 5 attempts, ~9700 VI rows each), same as s6411.
Work unit: read SOAK-RESULTS s6580_dd4_unsafe_lvl10/lvl1 (hold=301, vi_stalls30s=0, crashlines=0 => pass). If both pass, dd4 is clean on lvl1/5/10 -> decide lifting the s6446 cap (apply_s6036_dd.py:7) behind owner approval, then contact sheet dd1 vs dd4.
