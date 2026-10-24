# NEXT: G1d step 9 - who supplies colour-image address 0x8076A980 under FB_WIDTH=683
HYPOTHESIS-ID: g1d-widescreen
Known (s6116): w683 RDP SETCOLORIMAGE=0x8076A980 (683 wide) but VI flips 0x8066A980/0x805D5300; window black, VI origin stuck 0x66AD80.
Competing: H-second-ptr (another fb-pointer table, e.g. set by setupFramebuffers/ video-state fn, uses unpatched layout) vs H-pfm-order (pfm patch shifts later regions so a cached pointer from retail layout is stale) vs H-rt64 (RT64 mishandles 683 CI).
Discriminator: grep funcs_0.c for stores of region addresses returned by partitionFramebufferMemory and for 0x8076/0x76A980 constants; log at runtime the pfm return pointers + the CI address in the first flight DL (one build). Control: ctl run must show CI == VI flip buffer.
Screenshot recipe: scratch/agent/s6116_run.sh (reuse).
