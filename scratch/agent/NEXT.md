# NEXT (s7754)
HYPOTHESIS-ID: rdp-output-gate-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7753 landed tools/s7753_rdp_output_gate.py (sweep GREEN 2/2, controls tg0/cap/flip PASS) but it covers only 2 L1 21:9 dd8
in-flight tasks. Unit: widen coverage in ONE capture run, ONE build (no rebuild needed: ROGUESQ_S7751_SNAP already exists).
- Capture with ROGUESQ_S7751_SNAP armed (see tools/s7753_capture_snaps.zsh for the pose harness): (a) L1 dd1 retail settings
  in flight, (b) a hangar SELECT YOUR CRAFT frame, (c) a mission-intro cutscene frame (L4), (d) a 16:9 dd2 owner-recipe frame.
- Per snap record the live policy (CAP: 65536 at dd1 vs 1048576 at dd>1; TG_FIX default per dd) in a SNAPS table
  {path: (cap, tg_fix, tg0_len_or_None)}; the tg0 control applies only where TG_FIX=1 is live (dd>1); at dd1 use the cap and
  flip controls plus "TG_FIX=1 must differ or the task has no TriGen hits" (report tg_hits from the harness stderr).
- Hypotheses: H-exact (every new snap replays == live, gate extends cleanly) vs H-state (some path depends on state the snap
  does not carry, e.g. multi-task segment/overlay residency, so replay != live: name the missing state before excluding it)
  vs H-ucode-b (hangar/cutscene run a different ucode the lean harness does not link: then the gate must say so per snap).
Expected: H-exact for in-flight dd1/dd2; hangar is the likely H-ucode-b. Update the sweep regex snaps=N. Max 2 CPU-heavy jobs;
check the screen is unlocked (CGSSessionScreenIsLocked) before a key-driven pose run.
