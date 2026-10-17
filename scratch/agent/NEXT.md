# Next: m6-mission-soak — long in-mission flight soak with scripted stick/button input
HYPOTHESIS-ID: m6-mission-soak
Candidate (c) from the s5082 block, runnable locally. Build on scratch/agent/s5080_watch.sh (keyed route to
mission 0x620400, pad override file). Instead of 8 s holds, drive >=120 s of alternating W/S/A/D/Z/Return
inputs after mission onset (enqueue via soak_queue, 600 s cap per recipe; split if longer).
Verdict fields: crash count, VI advancing (last 20 s), ROGUESQ_PAD_LOG transitions == commanded, watch-log
distinct values of the 0x9DEAC triple (positive control: >1 in key windows, 1 in a no-key window).
H-stable: crash=0, VI advances throughout. H-late-fault: crash/stall/abort at a mission event under input
(then bisect by window). Do not combine with FREE_CENSUS (s5044). Single run = label n=1; repeat x2 for two-source.
Open non-gating human deps (no action): mips64-elf-gcc install; symbol-mapping source for renames.
Visible frame capture needs a screenshot path (macOS screencapture needs TCC = human setting) — not used.
