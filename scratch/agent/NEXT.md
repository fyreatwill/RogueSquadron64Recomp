# NEXT: G1d step 54 - menus/hangar under ROGUESQ_ASPECT=16:9 (title -> hangar route), then owner contact sheet
HYPOTHESIS-ID: g1d-widescreen
s6162: 21:9 in-flight frame verified. Work unit: run the TITLE_ORIGIN hangar route with ROGUESQ_ASPECT=16:9 and ROGUESQ_FB_DUMP_VI=1, inspect title/hangar fbdumps: H-ok (menus pillarboxed/correct), H-stretch (menus stretched or HUD anchor shifts menu elements), H-broken (clipped). If H-stretch/broken, add a per-screen policy (anchor only when in flight). Then build contact sheet 4:3/16:9/21:9 for the owner.
