# NEXT (s7828)
HYPOTHESIS-ID: g3-pose-input-time
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: s7827 closed the s7826 reticle offset as a camera-pose delta. The lvl1 flight sky mesh (PRIM 4FD926B9) fits a 0.115 deg pitch
difference, port vs cxd4/mupen retail (tools/s7827_tri_yshift_census.py --pose, controls PASS). The cause is inferred, not measured:
H-input-time (time-integrated sim state depends on frame/dt history; mupen's CPU timing is not hardware either) vs H-cpu-pose (a port
CPU defect in the camera/attitude math that changes the steady pose). Bounded: at most 2 iterations, then close single-source.
Discriminator (ground truth that is not our runtime): retail vs retail with ONLY the emulated CPU timing changed.
 1. Add `--count-per-op N` to tools/oracle/rs64_oracle.c (pConfigSetParameter(core_section, "CountPerOp", M64TYPE_INT, &n), next to
    RandomizeInterrupt ~line 4352). Rebuild with tools/oracle/build.sh. Positive control: the oracle log prints the value, and a CPO=1
    run reaches a given VI in less host time than CPO=2 / renders a different number of game frames per VI.
 2. Two retail-only rdplog captures on the s7826 route (retail half of tools/g3_menu_pair.sh, RENV as s7826, RSECS=150), CPO default (2)
    vs CPO=3 (or 1). One emulator at a time (CPU rule). Check both reach flight (tl.py bands: logo -> crawl -> 512 mission).
 3. `python3 tools/s7827_tri_yshift_census.py A.bin B.bin --win <flightA>,<flightB> --controls --pose <staticA>,<staticB> --p-retail`.
Outcomes: retail-vs-retail pitch |d| of the same order (>=0.0005 rad) -> H-input-time CONFIRMED (the pose depends on emulated timing;
the port delta is not a defect; close). Retail-vs-retail exact (d=0, sky identical) while the frame counts differ -> the pose is timing-
independent, so the port's delta is H-cpu-pose: next, dump the camera matrix (guest RAM) in both arms at the first flight frame.
If the route does not reach flight under the changed CPO, report that as the datum and close g3 det-pair work single-source.
