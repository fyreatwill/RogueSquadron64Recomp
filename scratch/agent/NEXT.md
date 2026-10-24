# NEXT: G1d step 14 - read s6121 aspect soaks (797 / 1045), then menus/hangar
HYPOTHESIS-ID: g1d-widescreen
Known: ROGUESQ_ASPECT=16:9|21:9 now derives FB_WIDTH/scales (s6121, main.cpp). Soaks queued: s6121_g1d_asp_16x9, _21x9; screenshots in scratch/agent/m6/s6121/ (view with Read).
Do: (1) read SOAK-RESULTS + screenshots. Undistorted wide frame at both -> allowlists generalise; black/garbage/crash -> grep 683/512/1024 width hardcodes in RT64 patch + game (stride, partitionFramebufferMemory sizing for 1045*448*2 vs flip spacing, 16 MB physical limit). (2) add a title/hangar arm (no force-level) at 16:9 to check menus. (3) HUD edge anchoring is next after that.
