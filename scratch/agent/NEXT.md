# Next work unit: capture counters at the setHudEnableBit4 hit
Rerun with a longer hold: env TRAPSWAP=2500 zsh scratch/agent/m6_objc_dump.sh s5475a 560 (s5474a at 330 s never reached the end; s5471a ended <420 s). Read the last samples before the setHudEnableBit4 stop (breakpoint 2): which of counter[2]>=3 / counter[3]>=9 / 0x8010B690.. words satisfied it. Legit if counters rose gradually; stale if they jumped from 0 at the hit.
HYPOTHESIS-ID: m6-mission-end-trigger
