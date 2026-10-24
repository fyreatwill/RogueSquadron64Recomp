# NEXT: G1d step 6 - fix the framebuffer overflow at widened width
HYPOTHESIS-ID: g1d-widescreen
Known (s6113): ROGUESQ_FB_WIDTH=683 (with VPW_SCALE=1.3333 ASPECT_SCALE=1.3333) makes scissor and SETCOLORIMAGE 683 wide and VI mode 683/xScale 0x444, but the fb readback is garbage. Colour images 0x80620000 and 0x80790000; the second ends 0x80823A00 > 8 MB top, masked/wrapped by RT64/dump.
Competing: H-overflow (buffer past 8 MB) vs H-dump-wrong-buffer/stride vs H-rt64-reads-VI-origin-with-other-stride.
Discriminator: one run, same recipe: (a) log the osViSwapBuffer fb addresses next to each dump and dump BOTH buffers; the 0x80620000 one (fits) should be a valid picture if H-overflow; (b) find the fb allocation (grep 0x80790000 / the video init) and move the upper buffer below 0x80700000 under the env. Then screenshot, then VI hstart/hend span for 16:9 and HUD x.
