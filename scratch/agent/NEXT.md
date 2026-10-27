# NEXT: fold s6357 sky-fade soak (G3c(a))
HYPOTHESIS-ID: g3c-owner-visual

s6357 soak queued (scratch/agent/soak_queue/s6357_g3c_skyfade.sh): arms nofade / fa (18..26) / fb (26..34), haze 139,189,213, dd3, LEVEL=1.
1. Read the SOAK-RESULTS line; compute g3c_edge_score per arm from scratch/agent/m6/g1_lvl1s6357_*/fbd.
2. View far-edge frames at the same phase; build an owner contact sheet nofade vs fa vs fb.
3. Outcomes: edge blends into sky -> keep that radius, wire as dd-scaled default under ROGUESQ_DRAW_DISTANCE; stair-step persists beyond radius -> footprint larger than fade radius, raise; no change -> haze not applied at those vertices, recheck colour (s6355 red ctl proved site live).
