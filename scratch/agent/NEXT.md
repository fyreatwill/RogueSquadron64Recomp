# NEXT: Next steps #4 - find the non-health mission-fail condition (s5733 H-OTHER) and land a change
Read PORTING-STATE s5733 and docs/CURRENT-TRUTH items 3-4. Hypotheses: (H1) timer/objective-bool fail (bool[1]/bool[7] writers), (H2) wingman/escort loss counter, (H3) port defect in a results-state writer.
Discriminator: static census of the results-state writer reached from the 0x64 fail arm + one entry log; mandatory pivot: commit a guard/code change or real-input route change, not another observation.
HYPOTHESIS-ID: g1-nonhealth-fail
