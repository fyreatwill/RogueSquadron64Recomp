# NEXT (s5682): fold s5681_pptr soak -> find ship object position/altitude
Run: python3 tools/pptr_fields.py scratch/agent/soak_results/s5681_pptr_*.log  (built s5681: [pptr] rows = 0x100 bytes of each KSEG0 pointer target in player record 0x137DB8, 1 Hz).
Positive control: pdump rows present and sx/sy vary (pdump_fields.py). Look for a (off,tgt) series with a vec3 whose delta correlates with stick (c>0.5) = position/attitude; altitude = its y.
Outcomes: found -> close the loop in the autopilot (level pitch); none -> follow one more pointer level or oracle watch; or switch to G2 audio comparison.
HYPOTHESIS-ID: g1-mission-progression
