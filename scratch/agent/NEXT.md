# NEXT (s7683)
HYPOTHESIS-ID: g6c-default-path-subs

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7682: tools/g6c_sub_handler_map.py closes the inline-draw audit for the 32 switch-installed stand-in subtypes (only 0x32 is off the
bucket path, hooked s7681). Remaining coverage gap: stand-in subtypes 0x33 0x36 0x44 0x4F (item+0x5C named, setupNpcUpdateFunctions
default case) were never seen in any [s7672-ho]/[s7679-life] log; 0x4B (same class) hands off normally.
Work unit (offline first, at most ONE run): (1) find which levels' DAT lists contain those subs: grep existing [s7623]/[s7679-life]
lines across scratch/s76*/ logs for `sub 0033|0036|0044|004F`; failing that, find the spawner that handles default-case subs (who
reads item+0x5C for them; grep jal sites that pass a DAT item and test lhu item+0 against 0x33/0x36/0x44/0x4F).
(2) If a level has one, one forced-level run (s7680 recipe tools/s7680_flight_release.zsh <out> <level>, STANDINS_LOG=1) and read
its [s7672-ho] lines.
Hypotheses: H-bucket (their real objects call addNpcToVisibilityBucket like 0x4B: real_add >= 0, nothing to do), H-inline (another
inline view-test path like the shield: held to near depth, extend the s7681 hook), H-absent (no level carries them: dead table rows,
leave as is). If H-bucket or H-absent: G6c engineering is done; it waits on the owner's look. Take the next rung (owner items 2-9, 20, 22).
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, no repeat-hold soaks.
