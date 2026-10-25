# NEXT: G1d step 35 - verify the 1024 clamp, then HUD edge anchoring
HYPOTHESIS-ID: g1d-widescreen
Build (DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build), run ROGUESQ_OSMEM_MB=12 ROGUESQ_ASPECT=21:9 (expect FB_WIDTH=1024, fbd w1024 frames, like s6142_w1024). Positive control: w1032 arm still garbage. Optional root-cause: grep 1024/0x400 in guest fb layout fn 0x80000DD4 and RT64 fb/texture limits. Then HUD edge anchoring, menus/hangar at wide, default OSMEM under ROGUESQ_ASPECT.
