# NEXT: G1e FPS60 float quanta - remaining named sites (s6826 fixed the guided-motion accel/drop)
HYPOTHESIS-ID: g3-fps60-float-quanta

Context: s6826 traced 253 per-tick float sites (tools/fixup_fps60_float_trace.py, ROGUESQ_TICK_TRACE) and scored them with
tools/g3_float_quanta_rates.py a30.bin f60.bin --sites <tsv from tools/g3_float_quanta_audit.py --tsv> (dR = f60/a30 median
per-tick |d|: 0.5 dt-scaled, 1.0 quantum). lvl14 only (lvl2 arms were cut off). Remaining dR 1.00 sites, unfixed:
  computeRandomizedOrientationFrame 0x800F372C +0x8C += 0x48*K*0x74, 0x800F390C +0xA4 += +0x78 (randomized orientation phase)
  minimalRandomNpcHandler 0x80060F2C/0x80060F3C +0x20/+0x24 *= const per tick (damping; needs pow(c, dt*30))
  timeSnapshotFiller 0x8000BD88 global 0x8012A8F4 += 1 (averaging divisor - probably benign, read its consumer first)
  hangarVehicleDisplayNpcHandler 0x800C6C9C/0x800C6CEC -= 0.00125 per call (hangar ship display; FPS60 hangar)
  updatePlayerVehicleByControlMode 0x8004D7CC (+0x18) dR 2.49 lrR 0.96 - unclear, path-dependent
Hypotheses per site: H-cosmetic (frequency/phase only; 2x at FPS60 is visible but harmless), H-gameplay (feeds motion or
timing), H-benign (consumer normalises it). Step 1 (offline): read each site's consumer, classify. Step 2 (one build):
extend tools/fixup_fps60_float_quanta.py with the H-cosmetic/H-gameplay sites (k = dt*30 for steps, pow for damping),
verify with the same lvl14 a30/fix/off recipe (scratch/s6826/verify.sh; run each 240 s arm as its own background
command or with timeout 1800000 - the 600 s default kills multi-arm scripts) plus lvl2 (scratch/s6748/lvl2.eep) for a
second level of the whole rates table. Done = every dR 1.00 site fixed or classified benign, on 2 levels.
