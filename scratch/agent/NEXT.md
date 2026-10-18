# Next work unit: M6 endurance runs 2 and 3, plus second-flight frame comparison
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5436): run a of 3 clean (1217 s hold, 0 crash, 0 stall, alive). Remaining: runs b and c (`env LATE=520 FBD_EVERY=400 zsh scratch/agent/m6_keyed_hold_post.sh s5437_b 1200`, run foreground-in-background one at a time; the soak queue's 600 s cap is too short for HOLD=1200). Then compare first-flight vs second-flight frames in scratch/agent/m6/*/fbd (hypothesis C). B = CRASH line or vi_stalls>0 -> capture backtrace (lldb) and name the writer.
