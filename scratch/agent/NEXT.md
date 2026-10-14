# Frame-aligned mission RDP diff: spliced 0x2C vs drop vs retail

HYPOTHESIS-ID: ovl2c-splice-mission-effect

Context (s4802): ROGUESQ_OVL2C_MODE 0=splice 1=drop 2=none is now a real switch (DROP was dead code). Submission counts at the mission phases do not differ across arms (phase 5/6 identical), so they cannot discriminate. Dumps exist: scratch/agent/s4806/m{0,1,2}.bin (port RDP, header {magic,lo,size,phase}; gitignored/untracked, regenerate with scratch/agent/s4806_modes.sh if deleted), retail mission RDP from s4733 (find rdp.bin under scratch/agent/s4733_*).
Hypotheses: H-splice-emits-sprites (m0 has texrect/tri content absent from m1 at aligned mission frames, retail has it too), H-splice-inert (m0==m1 content; 0x2C image produces nothing at this origin), H-other-writer (retail sprites missing in all arms because another op/overlay is unrouted).
Discriminating measurement: split phase-6 submissions into frames at fullsync/setcimg boundaries, align by frame ordinal from the first 0x690400 frame, and compare per-frame texrect lists (x,y,tile) of m0, m1, retail. Offline only (reuse s4806 dumps). Positive control: m2 vs m0 must differ at phase 3 (they do, 3x).
If the dumps cannot be aligned, rerun s4806 with a phase-gated cap (PROBE_PHASE_WIDTH) instead.
