# NEXT: fold s5762_slotwatch_lvsel — who sets slot state bit 0x8/0x10 (kill source)?
s5761 was VOID (plain route, 0 deaths, lives-watch control never fired). s5762 uses the level-select route (MISSION_RE=62BD00) where deaths occur. Read scratch/agent/m6/s5762_slotwatch_lvsel/lldb_att*.log and keys.log. Ignore summary wp_hits (counts list-echo lines); grep for `frame #` after the control stop.
Control: wp4 (lives 0x130B10) must stop+bt at least once; else void again (check keys.log for nomission/nohangar and run.log for [mtm] lives--).
Outcomes: wp2/3 bt top PC in collision/damage code = H1; timer/objective script = H2; stale value / stubbed-subsystem path = H3. If wp4 fires but wp2/3 never: slot base wrong (read a1 at runtime).
HYPOTHESIS-ID: g1-nonhealth-fail
