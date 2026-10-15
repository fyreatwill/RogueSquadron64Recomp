# BLOCKED (s4959)
Need: a human decision on how to run multi-minute game recipes inside an iteration.
Planned unit: repeat the s4958 keyed route (title->hangar->0x6A2900->~70s load->mission) x3 sequentially with PCM counters.
Tried: wrote scratch/agent/s4959_mission_x3.sh (3 sequential runs, 20+ min total) and launched it in the background. Run 1 had not reached the hangar and had written no keys1.log when the Stop hook blocked six times. The harness blocks foreground sleep/polling, so I could not wait for it within the turn. No result was obtained. The script and game were killed with SIGKILL.
Suggested: enqueue the recipe as three separate one-run soaks (the soak cap is 600 s per recipe, so the x3 script as written is too long), then consume the verdicts next iteration.
