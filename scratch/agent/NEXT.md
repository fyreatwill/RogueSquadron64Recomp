# NEXT: fold remaining G1 sweep soaks (levels 14b..18b), then (c) framebuffer captures

HYPOTHESIS-ID: g1-mission-coverage-sweep

Work unit: read the new SOAK-RESULTS.md lines for g1_lvl14b..g1_lvl18b (queued in
scratch/agent/soak_queue/). Any rc!=0, crashlines>0 or vi_stalls30s>0 is a datum:
capture a backtrace and name the writer. If all pass, pick one passing level and
add a framebuffer capture (G1 item c) to the recipe, enqueue it.
Open: level 10 `nomission` (stale cinematic state, curOvl=1 cineState=F7B80040).
