Work unit: fold s5517_wpflag_hangar_{a,b,c} soak verdicts (queued by loop; see SOAK-RESULTS.md and scratch/agent/m6/s5517_*/{summary,keys.log,lldb_att*.log}). Per run: did control 0x3470 fire, how many writes to 0x130B58 and with what values, any crash/stall.
Note (s5517): m6_wp_flag.sh is ALREADY hangar-gated (fails 'nohangar' without origin 0x006AB400); s5514 log has 551 hangar-origin lines, so s5515's "never set" already covers the hangar route (single run; a/b/c add replication).
Hypotheses: H1 bit 0x02000000 set on some run (route-dependent); H2 never set in 4/4 -> needs retail oracle or a different gate; H3 hangar route crash/stall.
If H2 holds 4/4: close the flag-word thread, pivot to second-mission selection by other means (docs/CURRENT-TRUTH next steps) or further M6 holds.
HYPOTHESIS-ID: second-distinct-mission-coverage
