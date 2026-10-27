# NEXT: fold s6446_dd3real_lvl5 / lvl10 (genuine dd3, 300 s each)
HYPOTHESIS-ID: g1c-phase2-dd3
Check each run.log (scratch/agent/m6/g1_lvl*s6446_dd3real/run.log) says "multiplier 3" (NOT capped) and alive_at_end=1, 0 crash lines, 0 VI stall. Clean on both -> dd3 qualified on lvl1/5/10; update docs/OWNER-OPT-INS.md and ask owner to judge docs/owner_sheet_s6439.png. A crash -> capture lldb backtrace, root-cause (finder null node, s6102). Lesson: always grep the knob echo in the log before trusting a recipe's label.
