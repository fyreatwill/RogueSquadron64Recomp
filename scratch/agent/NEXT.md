# NEXT: G1d hangar height + ASPECT flight holes
HYPOTHESIS-ID: g1d-aspect-hangar
Fold s6434_aspect_hangar219 (WIDE_ROUTE=1) from SOAK-RESULTS: rc, alive_at_end, stalls, crashlines.
Hypotheses: H-dump (rdram-re dump reads 448 rows but hangar FB is ~340 high -> artifact), H-viewport (hangar viewport/scissor height not scaled at wide aspect -> real bottom band), H-cap (ASPECT flight black rects = ucode iteration cap not scaled; s6403 scaled only for dd>1).
Discriminator: log hangar VI height/scissor at ASPECT vs 4:3 control in same build; run lvl1 flight at ASPECT=16:9 with ROGUESQ_UCODE_CAP=65536 vs default and count hole frames (g1c holes tool from s6405; control CAP=1500).
Then owner contact sheet (flight 4:3/16:9/21:9 + hangar), G3 livery diff, G5.
