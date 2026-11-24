# NEXT (s7896)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7895): island A closed by det_pair SNAP=c (crawl-keyed). Island B remains on all three scored missions, at the tail of the
640 pre-flight scene: m6 N212@6070 (scratch/s7895/m6k), m11 N1054@6062 (m11k), m3 N183@3760 (m3k2/m3c; flight starts 3943).
s7891 labelled B "state class" (tri-count / tri-geom diffs). Port bins + retail bins retained in those dirs.
Unit (offline first, no game run unless the read needs one):
  1. For each mission, list the first 5 non-exact frames of island B with s7868_det_frame_cmp.py --port-start <B-10> --port-end <B+30>
     on the kept bins: what differs (tri count, which colours/combiner, a whole object present/absent, positions)?
  2. Hypotheses: H-object (one object/actor appears/disappears a frame apart: spawn/despawn timing), H-dt (a scene clock offset again,
     e.g. another post-load frame in the 640 scene: check the [snap] fires and dt rows near B's VI), H-rng (a pre-flight rand call
     sequence: s7845 says ticks are exact from tick 0, but pre-tick rand calls differ: port 44520 vs retail 41341 calls before 1st tick).
  Discriminator: if the first B frame differs by a whole object -> find its spawn; if positions only -> clock (H-dt: dump the scene's
  dt struct like s7891_crawl_clock.sh with the right mark/struct); rand call count before tick 0 differing is a known pre-existing
  difference, only a lead if B's first frame is a random-placed object.
