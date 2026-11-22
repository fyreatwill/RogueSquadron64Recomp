# NEXT (s7831)
HYPOTHESIS-ID: g3-flight-residual-census
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: g3-pose-port-input is CLOSED (s7830). The s7829 arm-1 schedule (w1024 gate 11.5) gives a port capture whose steady lvl1 flight
pose matches retail (0/42 sky vertices >=0.5 px). With the pose matched, any remaining retail-vs-port difference in that flight band is a
real render/HUD/game residual, not camera pose. This is G3 render fidelity, OFFLINE (no game run needed): scratch/s7829/port.bin.zst vs
scratch/s7826/retail.bin.zst (and ret_off425/retail.bin.zst as a second retail reference).
Hypotheses:
 - H-exact: with the pose matched, world tris, HUD rects and moving sprites agree within 1 quantum (nothing left in this band).
 - H-residual-world: some world-tri class (terrain, objects, particles) still differs (texture/combiner/LOD or game-state difference).
 - H-residual-hud: HUD/sprite elements differ beyond the s7826 rate split (radar blips, reticle, counters).
Discriminator (one offline pass, all keys at once): `python3 tools/s7827_tri_yshift_census.py scratch/s7826/retail.bin.zst
scratch/s7829/port.bin.zst --win 3521:3825,4376:4695 --controls --pairs` plus `python3 tools/s7826_rect_path_offset.py
scratch/s7826/retail.bin.zst scratch/s7829/port.bin.zst --win 3521:3825,4378:4702`. Then repeat with ret_off425 as R (second line of evidence).
Break unmatched tris down by PRIM/texture class. Controls: the census planted controls must PASS. The s7826 pair (pitched) is the
positive control: it must show the 0.5 px reticle offset that the arm-1 pair should lose.
Outcomes: H-exact -> close lvl1 flight fidelity (two retail refs), take the next ladder rung. Residual class -> name it, write the
discriminator for its cause in the next NEXT.md.
