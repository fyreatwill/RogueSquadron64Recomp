# Which allocation do the HUD textures at 0xAE5F20/0xAE6B20 belong to, and does the wide wb/memset extent legitimately cover it?
HYPOTHESIS-ID: g1d-widescreen

s6215: writer named. Guest loadTextureToMemory (HUD ammo readout TLUT) writes 0xAE5F20/0xAE6B20; initVideoSubsystem rs_memset zeroes them; RT64 copyNativeToRAM wb (end=0xAE6E00) overwrites them with framebuffer fill.
Hypotheses: H-alias-wide (wide carve places the framebuffer/wb range over live texture memory that retail 4:3 does not overlap), H-alias-retail (4:3 also overlaps; harmless there because wb is skipped/short), H-memset-oversize (initVideoSubsystem memset length scales with widened w and runs past the framebuffer).
Discriminator, one build/one run per arm pair (ctl 4:3, wide 16:9, 12 MB): log (a) rs_memset dst/len when caller is initVideoSubsystem (guest regs a0/a2 via a fixup-inlined print, NOT lldb expression), (b) copyNativeToRAM dst/len (exists: [g1d-wb]), (c) loadTextureToMemory dst for the HUD descriptor. Compare ranges: overlap in wide only -> H-alias-wide (fix the carve so textures/framebuffer do not alias); overlap in both -> H-alias-retail; memset len > fb size only in wide -> H-memset-oversize.
Positive control: the ctl arm must print the same rs_memset call with retail dims.
Do not patch until the overlap is measured. Harness: scratch/agent/s6215_run.sh (lldb) works only with the interactive watchpoint-command form.
