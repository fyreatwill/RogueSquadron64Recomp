# NEXT: fold g1_lvl6u pair ([objsnap-t] with heartbeat control)

HYPOTHESIS-ID: g1-mission-coverage-sweep

H-C (state-gated tick, see s5961 addendum): hb absent => lvl6 is not in runInMissionFrame state 1, so the lvl6t null was a never-called hook. If H-C, log the jump-table state index per change on lvl6 vs lvl5 (lvl5 = positive control, must show hb).

Fold: `grep -h '\[objsnap-t\]' scratch/agent/m6/g1_lvl6{ctl,tele}/run.log`. FIRST check `hb ticks=` present in both arms (hook-ran control); if absent, tickMissionObjectives is not called on lvl6 flight - find the real per-frame caller. If present: tele-only ids => lvl6 (d) responds; none in both => H-B (forced hits do not reach the counter table). Then summarize (d) across lvls 1-9 and move to G3 render fidelity.
