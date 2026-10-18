# Next work unit: flown mission hold (autopilot flight + fire keys)
HYPOTHESIS-ID: m6-mission-endurance

s5418: 3/3 unflown 1200 s holds clean. Autopilot now has l,r,sl,sr,su,sd (src/main/main.cpp, built, untested).
Copy scratch/agent/m6_keyed_hold.sh to m6_flown_hold.sh. The autopilot caps at 64 events and a 512-char spec, so after the title/hangar z/start presses, replace the mash with a repeating pattern a,sl,a,sr,su,a,sd,r from ~t=100 s on.
Positive control: [autopilot] fire lines with nonzero stick/btn in run.log, plus fbhash distinct count rising. Run 2-3x at 1200 s (run_in_background, outside the soak cap).
Outcomes: CRASH/stall -> lldb backtrace, name the writer, root-cause fix; clean -> consider mission completion / second mission.
