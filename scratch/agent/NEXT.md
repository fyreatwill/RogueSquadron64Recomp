# NEXT (s5931): run g1_aim.sh with the wrap-latch + pitch-gain fix (already in main.cpp, rebuilt)

HYPOTHESIS-ID: g1-aim-autopilot-yaw-wrap

H-wrap: the +-180 deg flip causes non-convergence (fix should drop mean |yerr| well below the 124 deg control and min target distance below 24.5). If it still fails, H-rate (turn rate too low) is next.
Command: zsh scratch/agent/g1_aim.sh s5931_aim (screen unlocked), compare [aim] mean|yerr| ctl vs act, and [ctr1] sets.
