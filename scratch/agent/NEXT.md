# NEXT: fold g1_lvl6u pair ([objsnap-t] with heartbeat control)

HYPOTHESIS-ID: g1-mission-coverage-sweep

Fold: `grep -h '\[objsnap-t\]' scratch/agent/m6/g1_lvl6{ctl,tele}/run.log`. FIRST check `hb ticks=` present in both arms (hook-ran control); if absent, tickMissionObjectives is not called on lvl6 flight - find the real per-frame caller. If present: tele-only ids => lvl6 (d) responds; none in both => H-B (forced hits do not reach the counter table). Then summarize (d) across lvls 1-9 and move to G3 render fidelity.
