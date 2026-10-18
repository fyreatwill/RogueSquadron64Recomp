# Next work unit: make the a100 census valid (route + control) before reading it
HYPOTHESIS-ID: patcheslib-shadowed
s5369: two 300 s runs; hangar reached but mission (scanout 0x690400) not; head/walk a100 sites 0 in census and ctl; ctl never fires them -> no positive control for those sites, H2 untested.
Unit: (1) copy scratch/agent/soak_queue/done/s4849_m5_a10_guard_qualification_*.sh (known to reach mission ~185 s), add the a100 counter env + ROGUESQ_A100_CTL arms, grep 0x690400 first to confirm the route; (2) make CTL force the head/walk predicate itself (edit tools/apply_s5368_align100_counter.py) so ctl must print head/walk lines. Outcomes: ctl silent -> instrument broken; ctl fires + census 0 with mission reached -> H1 close; census fires -> read mis count, name writer.
