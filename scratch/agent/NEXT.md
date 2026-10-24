# NEXT: G1d step 8 - why 683-wide frames are garbage after non-overlapping buffers
HYPOTHESIS-ID: g1d-widescreen
Known (s6115): partitionFramebufferMemory patched (ROGUESQ_FB_WIDTH), spacing OK, dumps garbage; control (no width flag) dump valid.
Competing: H-rt64-vi-width (RT64 uses VI width/origin that disagrees with SETCOLORIMAGE width) vs H-second-hardcoded-512 (a copy/clear/Z loop or VI origin step with 512) vs H-dump-stride (dump/readback assumes stride from a different source).
Discriminator (one build): log at present: VI width reg, VI origin, SETCOLORIMAGE width seen by RT64/ucode, and game Z-buffer address/stride; also grep funcs for 0x200 / 1024-byte row strides near fb users. Positive control: same log on the no-flag run must show 512 everywhere.
