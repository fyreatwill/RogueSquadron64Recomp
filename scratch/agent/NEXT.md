# NEXT: what do the low-ground dd4 frames share? (dd4 ground deficit is intermittent)
HYPOTHESIS-ID: g1c-dd8-limit
s6487: pool x4 no effect (refuted exhaustion). dd4 ground med 0.734 here vs 0.235 in s6486; min 0.130 frames in both dd4 arms.
H-pose: low frames occur at specific camera poses/headings (pin drifts); H-timing: low frames are early (streaming not yet caught up after pin); H-data: low frames look at map edge where level data ends.
Discriminator: from existing dumps scratch/agent/m6/g1_lvl1s6487p_{d1,d4,d4p4}/fbd, compute ground score for EVERY dumped frame (not 13-sampled) vs frame index, plot series and find the low frames; check whether the same indices are low at dd1 (control) and whether they cluster at start. Offline only, no new run.
Same indices low in dd1 => pose/scene, not dd. Low only in dd4 and clustered early => streaming lag. Low only in dd4 mid-run => data/edge.
