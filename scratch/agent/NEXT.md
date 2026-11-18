# NEXT (s7589)
HYPOTHESIS-ID: host-resource-growth-audit

Class LK (heap) and OW/OW-2 (ObjC ownership) are closed. Sibling class HR: host resources that are not malloc heap.
Hypotheses: H-flat (all counts plateau after first mission load), H-fd (file descriptors grow per load / per save probe / per
audio hot-plug check), H-thread (threads or dispatch workers grow per hangar re-entry), H-port (Mach ports / IOSurfaces / Metal
resident allocations grow over time).
Method, ONE run, sampled from outside every 15 s (no build needed):
  lsof -p PID | wc -l (and by type), ps -M -p PID | wc -l, lsmp -p PID | wc -l (if lsmp present; else `sudo`-free
  `vmmap --summary PID` IOSurface / IOAccelerator rows), footprint PID.
Arms: (1) L4 dd4 16:9 FPS60 20 min hold, (2) s7469 hangar abort/re-entry route (3 re-entries, 4 loads, dd8 21:9).
Positive control: a plant that opens one fd per 1000 frames (add ROGUESQ_S7589_PLANT=1 in src/main, dup(2) kept open) must show
as a slope in the same run; without the control a flat count is not a result.
Fold: slope per minute after warm-up and per re-entry; any non-zero slope -> name the owner (lsof name / thread name / port
type) and fix it env-gated (=0 old). Reuse tools/s7585_memsample.zsh as the sampler skeleton.
Also fold the queued soak s7588_applepool_default (pass = alive, 0 stall, pool=0, plantD == plantA).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Owner may be at the machine: key-driven runs go
through the quiet-arms tool (exits 2 when a human is active) or the soak queue.
