# NEXT: G1e FPS60 float quanta - close the class (2 leftover sites + second level for guided motion)
HYPOTHESIS-ID: g3-fps60-float-quanta

Context: s6826 fixed guided-motion accel/drop, s6827 fixed minimalRandomNpcHandler scale growth (pow) and
computeRandomizedOrientationFrame phases (tools/fixup_fps60_float_quanta.py, verified lvl14 + lvl2). Left:
  updatePlayerVehicleByControlMode 0x8004D7CC (+0x18) dR 2.49 lrR 0.96 (step-mixed) - player vehicle, could be gameplay.
  hangarVehicleDisplayNpcHandler 0x800C6C9C/CEC -= 0.00125 per call - hangar, no dt captured outside the mission tick.
  guided-motion fix is verified on lvl14 only (no guided missiles on lvl2).
Hypotheses for 0x8004D7CC: H-dt (term is dt-scaled but a path-dependent value dominates |d|), H-quantum (part of the step is per
tick). Step 1 offline: read 0x8004D760-0x8004D7D0 (operand taint), compare the a30/f60 |d| distributions in
scratch/s6827/rates_*.txt sources. Step 2: if H-quantum, add it to fixup_fps60_float_quanta.py; for the hangar, find the hangar
frame dt (or count VIs per hangar tick) and scale. Verify: scratch/s6827/verify.sh (lvl14) + a level with guided missiles
(grep the s6826 rates for which levels run 0x8005F3C8, or lvl14 only + say so). Run each 240 s arm as a background command.
Done = every per-tick float site fixed or classified, then close G1e float quanta in CURRENT-TRUTH.
