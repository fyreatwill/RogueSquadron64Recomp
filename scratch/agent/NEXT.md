# NEXT: G1 - s5856: why do segment-in-sphere class-1 tests (s5855: 10 ids inside, 0 SEND) not become hit SENDs?
s5855: bolt line-sphere test passes for ~10 class-1 ids (id 18f: 295 inside) but SENDs only hit ids 52/c6/66. H8 refuted.
Hypotheses: H10 findSegmentObjectSphereHit returns 0 for them (clamped-segment miss; `in` over-counts as ap2 is line distance); H11 a pre-filter between the sphere test and the hit fn (flags/team/weapon-record id) skips class-1; H12 the bolts inside are NPC bolts, not player's (player id = s2, 0x38).
Discriminating measurement (one build, one run): at the call returning from findSegmentObjectSphereHit (0x8005D24C) log per cand id: return value, clamped sd2<=r2 count, proj +0xF8 weapon-record id, proj s2==player flag (0x38 per s5854). Positive control: existing SEND on id 52 must show ret!=0. Outcomes: clamped-in>0 & ret=0 -> H10 (inspect fn); clamped-in>0, ret!=0, no SEND -> H11; clamped-in only for non-player bolts -> H12.
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fireall.sh s5856 300
HYPOTHESIS-ID: g1-mission-progression
