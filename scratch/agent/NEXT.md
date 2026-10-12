# NEXT: does the hangar VI actually display column 511 of 0x656000? (close or confirm the col-511 thread)
HYPOTHESIS-ID: hangar-renderer-artifacts

s4641: 0x656000 draws only x=140..375; col 511 is stale prior-stride RDRAM nobody rewrites.
Hypotheses: H-vi-crop (VI hstart/hend excludes col 511 on retail so it is invisible there; our output path shows it), H-retail-clear (retail clears the buffer; we do not), H-benign (retail shows it too).
Discriminator: log VI hstart/hend/xscale/origin/width at the 512-wide VI in the hangar (one run, same script s4640_wbcol.sh plus env). Displayed right edge <=510 => our presenter is the leak (fix in presenter, not RDRAM); displayed edge covers 511 => H-retail-clear/H-benign, which needs oracle hangar reach (parked) -> close the thread as benign.
Positive control: same log at the 640-wide title VI must show its known extent.
