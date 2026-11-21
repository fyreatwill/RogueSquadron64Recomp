# NEXT (s7755)
HYPOTHESIS-ID: hangar-dl-midtask-rewrite
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7754 (CURRENT-TRUTH item 27): in the hangar the game CPU rewrites the craft display list's 0x04/0x02 vertex pointers
(0x8072xxxx -> 0x80739xxx, DL in 0x720000-0x753000) while the gfx thread's task reads it. Is it visible, and is it ours?
Hypotheses: H-invisible (live output differs from begin/end only sub-visibly) / H-port-timing (retail CPU patches only after the
task-done message, our gfx thread runs late or overlapped, so tasks read a half-patched DL -> holo shimmer/garbage; fix: order
the port's task vs the CPU) / H-retail-race (retail overlaps the same way; leave it).
Unit, mostly offline, ONE build if a run is needed:
1. Offline: tools/s7752_port_task/rdp_render on scratch/s7754/retained/hangar_hstate/k900_s1250.bin with (a) its live tail, (b) the
   begin-image replay, (c) the end-image replay (hybrid file as scratch/s7754/hstate.py builds); tools/s7752_render_diff.py a-vs-b,
   a-vs-c (--ctl). Count px >=8 LSB in the holo region. Sub-visible -> H-invisible, close (gate exclusion stands).
2. If visible: name the writer PC. One run of tools/s7754_capture_route.zsh (dd1, SECS=40) with a write watch on one of the
   rewritten words (e.g. ROGUESQ_DEBUG_WRITE on 0x80720144, see g3_optin_pose_arms.sh for the syntax) plus the task begin/end
   serials in the same log, so each write is placed before/inside/after a gfx task. Retail ordering: read the writer's caller for
   an osRecvMesg on the gfx-done queue before the patch (static, rogue_squadron64 disasm). Writes inside tasks with a retail wait
   before them -> H-port-timing.
Max 2 CPU-heavy jobs; screen must be unlocked.
