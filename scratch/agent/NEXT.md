Single next unit: fold the three queued soaks s5527_hangar_{a,b,c} (scratch/agent/SOAK-RESULTS.md tail; scratch/agent/m6/s5527_hangar_*/summary and keys.log). Count crashlines, vi_stalls30s, allattempts-failed per run. Same-run control: "mission t=" row plus fbhash distinct>1.
Hypotheses: H1 stable (0 crash/stall); H2 stall (VI origin frozen >30s); H3 new crash -> capture lldb backtrace (attach; launch fails getcwd EPERM), name the writer, fix root cause.
If all clean: M6 hangar route closed; pivot to generated-symbol-renaming revisit or render fidelity in flight (sky-only frames, OPEN per s5423 caveat).
HYPOTHESIS-ID: m6-mission-endurance
