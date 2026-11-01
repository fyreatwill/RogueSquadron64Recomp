# NEXT: G1d residual -- abort logo fly-out region shift (~5 swaps at 16:9/21:9)
HYPOTHESIS-ID: g1d-menu-sweep

s6731 pause-gated the s6158 radar-region shift, but the pause byte clears before the VI epoch changes, so the shift turns
back on for ~5 swaps of the abort-mission logo fly-out ([region-gate] lines in scratch/agent/m6/g1_lvl1s6731_f219/run.log).
s6732 closed the mission-start dark frame as non-G1d (also at 4:3).
Hypotheses: H-latch (once paused within an epoch, the shift must stay off until the next epoch: fix = latch the pause
gate per epoch in rs64_region_scan, dpc_bridge.cpp), H-benign (the fly-out tris are outside the radar region, nothing moves).
Discriminator, one build, one run: scratch/s6732/dense.sh f219 21:9 "ROGUESQ_LIVES_CAP=1 ROGUESQ_FB_DUMP_DIR=<abs>/fbd
ROGUESQ_FB_DUMP_EPOCH=<abort epoch from f219 log> ROGUESQ_FB_DUMP_VI=1" (adjust the dense window to the abort, ~t=225-235).
If any dumped fly-out swap has a shard in x 669..810 shifted +256 -> H-latch, land the latch with ROGUESQ_* =old switch and
re-run; if none of the ~5 swaps draws tris in the region -> H-benign, close G1d and move to G3 (first G3 item: RDRAM dump of
the mission-start intro-mode swap to decide RT64-vs-retail for its edge lines, s6732 entry).
