Work unit: M6 hangar-route coverage. Adapt scratch/agent/m6_wp_flag.sh (control = 0x3470 swap counter) to the hangar route (scratch/agent/autopilot_hangar_probe.sh recipe / in-process autopilot that reaches origin 0x006AB400), queue >=3 runs, keep only runs that reached the hangar.
Hypotheses: H1 flag word 0x130B58 bit 0x02000000 is set on the hangar route (gates second mission); H2 still never set (needs retail oracle); H3 hangar route crashes/stalls (capture lldb bt).
Discriminator: write-watch log with control firing; per-run crash/stall lines.
HYPOTHESIS-ID: second-distinct-mission-coverage
