# NEXT (s5917): bearing-to-nearest-class-1 sphere from s5901 rows (offline first)

HYPOTHESIS-ID: g1-mission-progression

s5916: open-loop stick windows did not raise class-1 crossings (3 vs 11 control). s5901 rows carry pp (player pos) and ctr (sphere centre) per row.
Work unit: offline on scratch/agent/m6/s5915_steer/run.log, for c1f=1 rows compute the bearing (xz) from pp to ctr and distance; tabulate vs plpos heading/velocity direction. Outcome: if class-1 spheres lie consistently off the ship's travel axis by a stable angle, derive the stick direction for a closed-loop steer script; if scattered, spheres are not aim targets and H-aim is closed.
Control: the 11 control-window crossings must show distance<=radius by the same calc.
