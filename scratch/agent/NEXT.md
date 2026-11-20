# NEXT (s7687)
HYPOTHESIS-ID: g6c-pos-fallback-neighbour

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7686: itemless pos callers now rejected for 0x0D/0x14/0x1E/0x1F/0x47 (ROGUESQ_S7686_POSSUB; L4 pair old 7 pos handoffs vs fix 0).
Remaining plain-fallback subs: 0x0C/0x24/0x2E/0x46, no pos callers on L1/L4/L5.
Work unit (close the thread): find levels carrying 0x0C/0x24/0x2E/0x46 (grep the stand-in table / DAT sub census, e.g.
tools/g6c_sub_handler_map.py output or rs64_standins.cpp table), run ONE level per sub that has the most of them:
  mkdir -p scratch/s7687/L<n>; env R=$PWD/scratch/s7687/L<n> HOLD=200 ALLOW_SLOW=1 ARMS="4:fix:ROGUESQ_STANDINS=1+ROGUESQ_STANDINS_LOG=1+ROGUESQ_FORCE_SAVE_MISSION=<n>" zsh tools/g1e_owner_quiet_arms.zsh
  python3 tools/s7686_pos_tally.py scratch/s7687/L<n>/log_fix.txt
Outcomes: itemless small-float callers -> add the sub to the reject set (H-neighbour) + same-binary pair; same-sub/real
itemless objects -> keep fallback (H-self); no pos lines anywhere -> close the pos-fallback thread as "no handoff risk".
Then build the G6c owner sheet (same-run on/off frames dd2/dd4, 2+ levels) if not already sent, and wait on the owner.
One game at a time, SIGKILL only, <=2 CPU-heavy jobs.
