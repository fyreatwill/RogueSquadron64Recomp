# G1d: clear the enlarged fb RDRAM span in the wide title
HYPOTHESIS-ID: g1d-widescreen
s6245: clamping writeback rows (256) did not blacken the lower half (0.998 non-black vs 0.819 ctl) -> noise is stale RAM, not RT64 writeback. 
Hypotheses: H-stale-ram (memset 0xB3B200..+900*448*2 once at fb alloc/ph4 start in rt64 or fixup -> lower half goes black); H-vi-width (VI reads w=512 of a 900 image; stride fix needed).
Discriminator: add ROGUESQ_WB_CLEAR=1 (zero that RDRAM span before the first ph4 draw), run s6244_run.sh with TAGX=_clear EXTRA_E="ROGUESQ_WB_CLEAR=1 "; compare lower-band non-black fraction (script in s6245 entry method) and VIEW the 512 VI picture. Control: TAGX=_ctl arm.
