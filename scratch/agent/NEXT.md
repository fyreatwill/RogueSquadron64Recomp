# NEXT: G1d step 10 - find the copy stage from the 0x8076A980 render target into the flips (w683)
HYPOTHESIS-ID: g1d-widescreen
Known (s6117): colour images/flips are consistent with the patched layout; VI origin fixed; flips still black/sparse.
Competing: H-tex-stride (copy uses SETTEXTUREIMAGE width/SETTILE line/LOADBLOCK dxt computed for 512) vs H-copy-dims (copy rect/scissor 512 wide) vs H-order (copy happens before render completes). 
Discriminator: extend tools/rdpbin_scissor.py (or new tool) to list, in ctl_rdp.bin and w683_rdp.bin (scratch/agent/m6/s6116/), SETTEXTUREIMAGE(0x3D) addr/width, SETTILE(0x35) line, LOADBLOCK(0x33) dxt, TEXRECT(0x24) following a SETCOLORIMAGE to a flip. ctl vs w683 diff of that table selects the hardcoded-512 field. Positive control: ctl must show textures sourced from 0x80790000.
