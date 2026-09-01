# M5 Session 3535 — AI-frequency contract validation

The host `osAiSetFrequency_recomp` implementation now computes
`dacRate = round(48681812 / frequency)` and returns `48681812 / dacRate`,
matching the retail contract identified in Session 3534.

The Debug target rebuilt successfully after exporting the submodule patch. One
real-audio LLE/spin-yield/autopilot run fired the startup AI positive control,
reached title VI 1024 (`0x00790400`) and hangar VI 512 (`0x006AB400`), and
reported phase-keyed setup rows with input `0x5622` and return/store `0x561F`.
No crash marker appeared before the required SIGKILL watchdog termination.

This validates the contract correction and preserves the qualified route. It
does not identify the next image-task/output edge.
