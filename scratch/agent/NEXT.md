Single next work unit (s5593): fold s5592_m6_long_g,h,i (queued; loop runs them; do NOT run the game).
Commands: grep -n s5592 scratch/agent/SOAK-RESULTS.md ; grep -E "CRASH|abort|stall" the logs.
Outcomes: any CRASH/stall -> capture backtrace, name writer, root-cause fix. All clean -> extend M6 to second mission / hangar route.
HYPOTHESIS-ID: m6-mission-endurance
