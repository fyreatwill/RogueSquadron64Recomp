# Session 5297 M4 task-keyed retail join

The cxd4 RSP probe was extended with a monotonically increasing task serial.
The serial is emitted in both the `RSM1` mid-task record and the `RSD1`
completion record. The qualified 75-second retail route was rerun with the
existing VI trace, whole-RDRAM watch, and input schedule.

Controls passed: four VI width transitions, two whole-RDRAM watch-hit markers,
3,020,766 mid-task records, and 2,083 graphics completion records. Every one
of the 2,083 graphics task serials joined; no mid-task serial was unmatched.

Of the joined tasks, 1,222 contained at least one signed `-32768` (`0x8000`)
VACC lane in a mid-task sample. The samples came from many RSP PCs, not one
isolated site. All 2,083 completion records had zero `0x8000` lanes.

This refutes the prior task-key failure (H3) and establishes retail per-task
prevalence and completion state. It does not select H1 versus H2 by itself:
the retained port capture is row-capped and is not task-keyed at comparable
coverage. No mitigation follows. The next discriminator is a matching
task-keyed port capture.
