# NEXT (s7675)
HYPOTHESIS-ID: g6c-standin-ghost

s7674 closed the held-cull question (all off-screen). First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report
outranks everything), then any owner report.
Unit: G6c ghost stand-ins. In s7674 (scratch/s7674/log_x4.txt) L4 item 80547410 spawned at frame 2462, its stand-in was held 601
frames (the cap) and ACCEPTED 321 of them, but the real object never called addNpcToVisibilityBucket (real_call=-1, re_rej=0).
Hypotheses: H-dead (the object was destroyed or hidden right after spawn, so the stand-in draws an object that is not there: a
real defect, fix = stop the hold when item+6 / health / unlinked says so), H-miss (the real object did draw, but neither the
state+0x34 item match nor the 2-unit position match caught it, e.g. it moved >2 units: a matching gap, harmless on screen but
then it is a double draw), H-other-path (the real object draws through a path that does not use the bucket).
Discriminator, one build: for held stand-ins with real_call<0 after 30 frames, log once per second the item's +6 / +0x6C health /
linked state and the nearest real bucket call position (min distance over all real calls that frame). H-dead = health<=0 or
unlinked; H-miss = a real call within ~10 units; H-other-path = alive, linked, no call near. Control: s7672 PLANT rows.
Recipe: zsh scratch/s7672/run.zsh scratch/s7675 4 odd (now absolute outdir), score with tools/s7672_handoff_score.py.
One game at a time, SIGKILL only, never touch build/saves, <=2 CPU-heavy jobs, no repeat-hold soaks.
