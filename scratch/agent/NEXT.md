# Next work unit: read m6_mission_v2_c verdict; harden M6 stall detector, verify in-flight
HYPOTHESIS-ID: m6-mission-endurance

s5410: v2_a/b clean (0 crash/0 stall, ~440 s). Remaining doubts: stall detector counts any "origin=" line (debug spam masks a VI freeze) and no positive control; unknown whether scene is flight or briefing.
Do: (1) read v2_c line in SOAK-RESULTS; (2) edit tools/agent/m6_mission_tmpl.sh.in to count only '^\[phase\]' / true VI origin rows and add a SIGSTOP-free positive control (e.g. grep rate sanity); (3) add a screenshot or scene-marker grep to tell flight from briefing; (4) enqueue 3 v3 segments; CRASH => backtrace, writer, root-cause fix.
