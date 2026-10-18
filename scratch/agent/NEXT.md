# Next work unit: mission-end / results-screen transition endurance
HYPOTHESIS-ID: m6-mission-transition-endurance
- Plume guard thread closed as "guarded, unproven" (s5448: natural fire 0/9, forced-zero control 3/3 survivable).
- z-only flight never ends the mission (s5445). Find a recipe that completes/aborts the mission (e.g. menu quit via pause without MISSION GOALS overlay, or long flight with fire keys) and hold >=120 s past the transition, logging crash/VI stall.
- Discriminate: crash/stall after transition (H1 real defect, take backtrace) vs clean (H2 transition fine) - needs a control proving the transition occurred (VI origin change / mode change in log).
