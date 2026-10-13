# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

s4731 closed the hangar-reference thread (RDP diff already done s4517-s4521; Rice screenshots invalid as pixel reference; oracle has --shot now).

Work unit: port mission-phase correctness with the s4724 recipe (scratch/agent/s4724_run.sh reaches retail initMission at 73.4 s, mission VI 512 @0x690400/800). Run the port on the same schedule, phase-gated on the mission VI transition, compare to retail: per-sync RDP histogram first (as s4515), then aligned-frame byte diff with scratch/agent/s4517_diff.py.
Hypotheses: H-stream-equal (port mission stream matches retail, defects renderer-side); H-rsp (shade/geometry words differ, another RSP idiom defect); H-route (port cannot reach mission; s4657-s4670 never did, need a route discriminator first).
Discriminator: per-sync tri/texrect counts + first differing command at the first aligned mission frame. Positive control: retail vs itself zero diff; hangar frame vs mission frame nonzero.
