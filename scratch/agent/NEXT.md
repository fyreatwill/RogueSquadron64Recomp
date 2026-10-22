# NEXT (s5919): per-object range/heading table for the ~6 class-1 objects

HYPOTHESIS-ID: g1-mission-progression

Context (s5918): class-1 hits come from ~6 moving objects (80357830, 80357ef0, 8021d474, 80359000, 8021df00, 8021f580). pp is the ship track. Bearing vs velocity cannot say whether the ship ever points at them.
Hypotheses: H-range (class-1 objects never get within bolt range ~ dl of the ship's line), H-heading (in range but ship heading off-axis), H-lifetime (objects exist only briefly).
Work unit: offline first - from s5915_steer/run.log tabulate per class-1 obj: first/last log order, min |ctr-ship|, rows. If most have min range > bolt reach, H-range; else add ship heading (obj+? yaw) to the [plpos] emitter (main.cpp ~9967), rerun tools/g1_steer.sh, and compute angle between heading and ship->obj.
Control: c1f=0 shape / 398 c1f=1 rows reproduced.
