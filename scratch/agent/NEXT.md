# Next work unit: keyed mission endurance confirmation (M6)
HYPOTHESIS-ID: m6-mission-endurance

Clear any macOS UserNotificationCenter crash modal first with
`pkill -KILL UserNotificationCenter`. Run the existing keyed mission-hold
recipe one at a time:

`zsh scratch/agent/m6_keyed_hold.sh s5394b 900`

then repeat for `s5394c`. Confirm each log contains a preceding hangar VI
origin `0x006AB400` before accepting mission `0x00690400`; this distinguishes
playable mission entry from the attract demo.

Competing hypotheses:

* H1: the qualified route is stable beyond the first 600-second hold; both
  runs stay alive with no crash and no unchanged VI origin for 30 seconds.
* H2: a distinct mission crash or stall remains; a failure log plus lldb
  backtrace names the writer and becomes the next root-cause fix.
* H3: the route is still not keyed into playable mission; the hangar
  prerequisite or key positive control fails before the hold begins.

Discriminator: per-run hangar prerequisite, mission-arrival verification,
CRASH/abort count, and VI-origin stall count. Use SIGKILL for watchdog cleanup.
