# Why do 150 s runs sit at VI 640 (stalled=1) instead of reaching VI 512/hangar?

HYPOTHESIS-ID: vi640-stall-vs-512

s4790: both DROP arms ran crash-free at load 7-20 but stayed at VI 640 (update_screen #9536, `vi-fs-decision SKIP stalled=1`); s4787/s4786 default runs reached VI 512 within ~150-240 s. Work unit: run the default binary (no DROP, ROGUESQ_LOG_PHASE=1, idle, no key presses) for 300 s, three times sequentially, recording per run: time of the first vi_width=512 line (or none), and crash/no crash. Control: s4786's recipe (scratch/agent/s4786_default_check.sh). Outcome: 512 reached in some runs => stall is timing/load dependent, gate mission work on a 512-reached check; never reached => something differs from s4786 (check env flags LLE_FORCE/UNGATED/SOLO/DLWALK vs the s4786 script).
