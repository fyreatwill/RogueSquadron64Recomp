# Next work unit: M6 residual - rare-route variation + plume title-boot loop
HYPOTHESIS-ID: m6-mission-transition-endurance
- s5449: 1203 s post-results hold clean (4/4 transition runs; transition endurance is NOT untested - s5436/5437/5449). Do not repeat plain post-results holds.
- Next: queue a title-boot loop (>=20 boots) with the in-process crash handler to catch the plume SIGSEGV (si_addr=0x58) backtrace; or vary the mission (hangar select different mission via d-pad before 'a') with a >=900 s hold, logging origins reached. Control: new origin set vs s5449's list.
- Run long holds directly (loop soak cap is 600 s).
