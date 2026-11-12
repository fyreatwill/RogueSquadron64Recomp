# NEXT: Retina / 4K render scale (G1f item 4, "internal resolution follows the window so a 4K TV is sharp")
HYPOTHESIS-ID: retina-render-scale
Context (s7202): lib/rt64/CMakeLists.txt:77 sets PLUME_APPLE_RETINA_ENABLED OFF, so plume_apple.mm getScaleFactor() = 1 and
the Metal swap chain is the window's POINT size. Built-in launch with ROGUESQ_ASPECT=16:9: SDL drawable 2720x1528 at create,
RT64 swap chain 1360x764 (scratch/s7202/bi.log + bi.ring Z rows). RT64's internal resolution (ROGUESQ_RESMULT / auto) is
derived from the swap chain size, so on any 2x display the 3D image is rendered at half the panel's pixel count.
Hypotheses:
- H-half: RT64 renders at points; CoreAnimation upscales 2x (soft image). Turning Retina on gives a 2x swap chain and sharper frames.
- H-resmult-covers: ROGUESQ_RESMULT already renders the scene above the swap-chain size, so only the final 2D/UI blit is soft.
- H-retina-breaks: Retina ON was disabled upstream for a reason (window-size math, mouse coords, fullscreen size, VI aspect).
Discriminator, one build with a runtime switch (ROGUESQ_RETINA=1 in getScaleFactor instead of the compile flag, default off
until measured): on the built-in panel windowed and fullscreen, arms RETINA=0/1: swap chain size (Z rows), RT64 internal
resolution log, frame cost (Q rows gpu_ms), and a crop of a fixed frame (title / FACTOR 5 logo at the same VI phase) to
compare edge sharpness (high-frequency energy). Plus fullscreen on the 1x virtual display (tools/virtual_display.m) as
the control: RETINA=1 must change nothing there. Owner decides the default.
