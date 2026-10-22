# NEXT (s5931): calibrate ROGUESQ_AIM yaw axis

HYPOTHESIS-ID: g1-aim-autopilot-yaw-calibration

H1 yaw sign inverted; H2 wrong matrix column/row for forward; H3 turn rate too low/yaw wrap bug.
Discriminator: in ONE run, hold sr alone for 20 s then sl alone for 20 s (A held), log forward-vector yaw per sample; sign and rate of d(yaw)/dt split H1/H2/H3. Then fix the law in main.cpp ~10009 and rerun scratch/agent/g1_aim.sh; success = mean |yerr| actuated << control and class-1 [ctr1] get(1) rises.
