# NEXT: G1 — win mission 1 through real input

Work unit: run the existing real-input mission-1 route with a keyed flight hold and
mission-win controls, then inspect the captured log and phase/frame markers. Do not
use `ROGUESQ_MISSION_WIN` as the pass condition; a pass requires a legitimate
mission completion/advance path. The route must reach flight, remain unlocked and
screen-unlocked, and run at least 10 minutes or until a legitimate win/failure.
Record every distinct crash, abort, VI-origin stall (>30 s unchanged), or softlock.

Competing hypotheses:
- G1a: the route can complete mission 1 with real controls; expect a legitimate
  completion and transition to the next mission/menu.
- G1b: the port remains alive but the objective path cannot complete; expect a
  stable flight followed by failure/restart without a win.
- G1c: a distinct mission subsystem crash/stall/softlock prevents completion;
  expect a reproducible failure marker and a backtrace-oriented follow-up.

Discriminator: the mission-completion transition itself, keyed by phase/VI and
not wall-clock alone. G1a selects progression; G1b selects objective/input
logic; G1c selects a new crash/stall work unit. Use the existing real-input
recipe/launcher under `tools/agent/` or queue a self-contained recipe under
`scratch/agent/soak_queue/`; launch from `build/`, capture to a non-dot final
path, and SIGKILL the process group. Check screen lock before key-driven input.
HYPOTHESIS-ID: g1-mission-progression
