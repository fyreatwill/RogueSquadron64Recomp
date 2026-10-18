# Next work unit: repeat keyed mission holds (M6)
HYPOTHESIS-ID: m6-mission-endurance
s5394a: 1 clean 600 s hold (mission seen t=168 s, 130 s verify ok). Kill any UserNotificationCenter modal first (`pkill -KILL UserNotificationCenter`).
Run `zsh scratch/agent/m6_keyed_hold.sh s5394b 900` and s5394c (one at a time). Also confirm the hangar row 0x6AB400 precedes the mission in run.log (guards against attract-demo false positive).
Outcomes: all clean => lengthen to 30 min and play inputs; any CRASH/stall => capture lldb backtrace, name the writer, fix root cause.
