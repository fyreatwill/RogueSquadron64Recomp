# NEXT: fold pose-pinned dd2/dd3/dd4/dd6 arms and find where the ground disappears
HYPOTHESIS-ID: g1c-dd8-limit

Queued: soak_queue/s6469_dd_break_sheet.sh (dirs scratch/agent/m6/g1_lvl1s6469p_d2/d3/d4/d6; controls g1_lvl1s6468p_d1 (ground present) and _d8 (missing)).
Work unit: after the soak lands, `python3 tools/g1c_ground_sheet.py scratch/agent/m6/s6469_pinned.png dd1=..s6468p_d1 dd2=..s6469p_d2 dd3=..s6469p_d3 dd4=..s6469p_d4 dd6=..s6469p_d6 dd8=..s6468p_d8`;
use tools/g1c_fbdump_join.py to confirm same-phase pairing first. Break at dd N -> test that step's pool/DL/vertex counters
(LOG_F5_STORE_SHADOW in run.log); no break below dd4 -> dd4 jump is the lever. If a pinned arm fails to pair with d1, the score is invalid again.
