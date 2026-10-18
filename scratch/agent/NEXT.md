# Next work unit: route variation for M6 endurance
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5438): frame md5 comparison is uninformative on animating scenes; visual check shows flight 2 renders like flight 1 (single-source). Keyed hold recipe saturated 3/3 clean.
1. Queue soaks (scratch/agent/soak_queue/) on the hangar route and an alternate key schedule, >=600 s hold, >=3 runs; log every CRASH/abort and stall (VI origin unchanged >30 s).
2. Any distinct failure: capture lldb backtrace, name the writer, fix root cause.
Helpers: scratch/agent/m6/ppm2png.py out.png in.ppm... (vertical montage), frame_stats.py <rundir>.
