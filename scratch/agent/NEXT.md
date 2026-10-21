# NEXT: G1 — which objective never advances under real input

Work unit: rerun g1_armA.sh-style hold (HOLD=600) with the objective instruments
armed (ROGUESQ_LOG_HUDBIT=1, [ccosnap]/[objbool] logs) added to COMMON, then
tabulate boolean-array snapshots over time (kills counter, waypoint, timer).

Hypotheses: (a) enemy-kill objective never increments because our autopilot
never hits targets; (b) objective advances but win check is gated on a bool the
port never sets; (c) mission timer/fail path fires first. Discriminator: which
booleans change between mission onset and the end, vs the retail oracle if
reachable. Positive control: the snapshot must show at least one boolean change.

HYPOTHESIS-ID: g1-mission-progression
