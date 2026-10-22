# NEXT: G1 - s5865: fold soak s5864_stick_pdump (record state vs stick while ship pos is frozen)
Context: s5864 refuted H25/H27 (axes delivered and consumed: record echoes +0xDC/+0xE0, pos.y tracks sy). Frozen translation is a state gate (H26).
Read: scratch/agent/SOAK-RESULTS.md tail for s5864_pdump; log in scratch/agent/m6/s5864_pdump/run.log ([pdump] rows + [plpos]).
Hypotheses: H26a steering state live (echoes/+0xD0 track stick) but translation gated -> thrust/ground gate (find who zeroes speed; A sets it); H26b record dead too (ship inactive/crashed, awaiting respawn) -> find crash-state flag; H26c pdump row count 0 (origin gate) -> control failed, rerun.
Discriminator: during the su/sr/sd windows (el 240-360) compare tools/pdump_fields.py correlation of +0xDC/E0/+0xD0 with stick against plpos delta (=0). Control: same fields correlate in the a-window or early window.
Then: if H26a, grep CURRENT-TRUTH/ game-architecture for speed/throttle field, dump it across the a-window vs none-window.
HYPOTHESIS-ID: g1-mission-progression
Also: backtrace Bus error far=0x3c2d5b616 / 0x37fffd040 (M6) when a run recurs it.
