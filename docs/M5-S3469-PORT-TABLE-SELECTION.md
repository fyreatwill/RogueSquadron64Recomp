# M5 Session 3469 — port table selection

The port witness was installed through `tools/apply_s3469_m5_table_selection.py`
and rebuilt successfully. The autopilot run reached title origin `0x00790400`
at width 1024 and hangar origin `0x006AB400` at width 512. The existing
four-PC output/state schema control fired, and the witness emitted 2,048
table-selection rows: 1,024 at `0x800644DC` and 1,024 at `0x80064524`. The
existing output/state witness emitted 2,048 rows and its positive control fired.

At title, the port selected live `0x801Bxxxx` entries, including
`0x801B4AA0 -> 0x801B4F00` and `0x801B4B20 -> 0x801B5E70`, matching the known
retail pointer family and values from the independent Session 3468 baseline.
This does not support a port-side table-pointer-family divergence; the
remaining qualified hypothesis is a value/output-state contract divergence
after this boundary. It does not yet provide an ordinal cross-runtime join.

The first two oracle attempts passed the whole-RDRAM positive control but stayed
at 320-wide attract and produced no target rows, so they were not treated as
null evidence. The port capture was SIGKILLed after the window with no crash
marker.
