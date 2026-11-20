# NEXT (s7702)
HYPOTHESIS-ID: post-g6c-owner-wait-s7702

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
Step 0: CURRENT-TRUTH is ~59.98 KB, right at the 60000 trigger. If `wc -c` > 60000: MAINTENANCE only. Migrate the s7660-s7701 headline and the
G6c detail to PROJECT-OVERVIEW, renumber Next steps, do nothing else.
Otherwise, candidate (21:9 follow-up from s7701): does skipping the 768-wide RDRAM write-back at 21:9 matter to the GAME? s7701 found RT64
drops `[ost-wb] SKIP_WILD_W w=768` for the 21:9 playlist buffer (allowlist 320/512/640/1024 + ROGUESQ_FB_WIDTH, lib/rt64 rt64_state.cpp:282).
The 16:9 flight width is also 768 (s6885), so 16:9 owner flight may skip it too: count SKIP_WILD_W widths in one existing 16:9 owner-mode log first
(grep -a 'SKIP_WILD_W' scratch/s7700/movd2/run.log | awk '{print $6}' | sort | uniq -c), no run needed.
Hypotheses: H-unread (the game never reads its colour buffer back, so the skip is harmless) / H-read (some effect, e.g. a screen wipe or
pause backdrop, copies the framebuffer and shows stale RAM at wide aspect).
Discriminator: one oracle-free check, the game reading the buffer. Log reads from the skipped buffer range (RDRAM load watch on its phys range
during a wide cutscene, or LoadBlock/LoadTile from a texture address inside the colour image range in the F5 RDP stream). Positive control:
the same watch on a 640 buffer at 4:3. If H-read, add 768 (and the 21:9/16:9 aspect widths) to the allowlist under an env and compare frames.
