# Next work unit: read M6 mission-endurance segment verdicts, root-cause the first distinct failure
HYPOTHESIS-ID: m6-mission-endurance

Enqueued s5408: scratch/agent/soak_queue/m6_mission_seg_{a,b,c}.sh (template tools/agent/m6_mission_tmpl.sh.in; key gaps 4/6/9 s; 555 s deadline).
Read: tail SOAK-RESULTS.md, then scratch/agent/soak_results/m6_mission_seg_*/keys.log (+ crash_excerpt.txt).
Outcomes: SCREEN-LOCKED => unlock, re-enqueue (result meaningless). nohangar/notitle in all => route flake, not a game finding; lengthen key loop.
mission-onset + clean summary (crash=0 stalls=0) => hold is clean for ~5 min; raise DEADLINE via a second launch phase or stack segments.
CRASH => backtrace from crash handler (main.cpp ~10078), name the writer, root-cause fix (PatchesLib C patch allowed, two-arm qualification).
STALL => capture VI origin + last log rows around the stall; check threads via crash handler/sample.
