# NEXT (s7703)
HYPOTHESIS-ID: wide-fb-readback-s7703

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
Step 0: CURRENT-TRUTH is 60365 B (> 60000) after s7702, so this iteration is MAINTENANCE ONLY: migrate the s7660-s7702 headline and the G6c detail
to PROJECT-OVERVIEW, renumber Next steps, do nothing else.

After maintenance, the follow-up to s7702 is: does the 21:9 write-back skip CHANGE THE PICTURE in the boot cinematic window (t 12.0-16.7 s), where the game
copies its previous 768-wide frame (4 KB LOADBLOCK chunks from 0x9B6000/0xA35800, both SKIP_WILD_W targets)?
Hypotheses: H-gpu (RT64 resolves the texture from its own GPU framebuffer, so the picture is the same with or without the write-back) / H-stale (RT64
reads RDRAM for it, so 21:9 shows stale or cleared RAM in the copied part of the image) / H-partial (only some frames or rows differ).
Discriminator: presented frames (not FB_DUMP, which reads RDRAM) through the cinematic window at 21:9, default vs ROGUESQ_ALLOW_WILD_W=1, phase-gated
on VI count from boot (no stopwatch), plus a 4:3 reference of the same window. Run them one after the other. Name the cinematic shown at t 12-16.7 (G5d
Factor 5 logo is a candidate). Positive control: the 4:3 arm (640, write-back allowed) must show the copied content. If H-stale: add 768 (the 21:9 cinematic
width) to RT64's rs64_writeback_sane allowlist (lib/rt64 rt64_state.cpp:282) behind the aspect setting, then export.sh + commit in the same session.
Also rerun the s7702 census at 21:9 with the DMA hook now live (ROGUESQ_S7702_FBREAD arms it as of s7702) to cover RSP DMA reads in that window.
