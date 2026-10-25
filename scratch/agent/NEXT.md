# NEXT: G1d step 34 - find the first failing FB width between 896 and 1045 (suspect 1024 cap)
HYPOTHESIS-ID: g1d-widescreen
Known (s6141): at OSMEM 12 and 16 alike 21:9 (w1045) never reaches a wide frame; 18:9 (w896) and 16:9 (w796) render correct flight. Memory refuted.
Hypotheses: H-width (constant 1024 cap/stride/texture-size limit in game, RT64 or ucode), H-aspect-math (21:9 projection value only), H-other-threshold.
Discriminator: copy scratch/agent/s6141_run.sh; arms at OSMEM=12 with explicit ROGUESQ_FB_WIDTH=960, 1024, 1032 (plus ASPECT_SCALE/VPW_SCALE as main.cpp:10733 derives for 21:9 - or ASPECT=<w>:<h> chosen to give those widths, e.g. 20:9=996?). Judge by fbd widths. First failing width selects the constant; grep 1024/0x400 in RT64 allowlists (s6119 width allowlists) and the guest fb layout fn 0x80000DD4.
Then: HUD edge anchoring, menus/hangar at wide, bundle OSMEM default under ROGUESQ_ASPECT.
