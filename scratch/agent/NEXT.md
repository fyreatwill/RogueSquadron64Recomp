# NEXT: G4 crash/stall hunting across missions (G3 in-flight coarse-closed)

HYPOTHESIS-ID: g4-mission-soaks
Write queued soaks (scratch/agent/soak_queue/) re-running lvl1-9 forced-route recipes (see done/ g1_lvlN_zs.sh) for 600 s with keyed hold, checking each for CRASH/VI stall. Alternatively a pixel-level G3 diff needs a port lvl1 start-of-mission fbd dump matching retail camera (retail frame docs/g3_retail_lvl1_flight_oracle.png).
