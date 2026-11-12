# NEXT: display hot-plug (owner plays fullscreen on a 65" TV; s7201 closed the pad side)
HYPOTHESIS-ID: input-display-hotplug
Context: s7201 added always-on witnesses in the SDL event watch (src/main/main.cpp create_gfx): `[g1f] display changed -> N`
(SDL_WINDOWEVENT_DISPLAY_CHANGED) and `[g1f] display event E display=D` (SDL_DISPLAYEVENT: 1 orientation, 2 connected,
3 disconnected). Nothing reacts to them yet. G1f item (3) "moving between displays" was "if feasible" and never measured.
Read first (offline): update_gfx fullscreen toggle path, what ASPECT=auto / RESMULT read at startup only vs per resize
([g1f] resized handler), and RT64 swapchain resize on drawable change.
Hypotheses:
- H-display-dead: a fullscreen window whose display is removed stays sized for the old display (wrong drawable / black).
- H-display-follow: macOS moves the window to the remaining display and SIZE_CHANGED -> RT64 resize handles it.
- H-aspect-stale: the window follows, but ASPECT=auto's FB width / RESMULT stay at the old display's values.
Discriminator: a virtual display created/destroyed from a tool (CGVirtualDisplay private API, tools/virtual_display.m,
unsigned build; test it creates a display visible in `system_profiler SPDisplaysDataType` first = positive control).
Arms in one script: fullscreen ROGUESQ_FULLSCREEN=1 ROGUESQ_WINDOW_POS on the virtual display, destroy at t=15 s; log
[g1f] lines, drawable size, presented-frame cadence ([g1b]); ctl = no destroy. If the private API does not work unsigned,
fall back to a code read + an SDL_WINDOWEVENT_DISPLAY_CHANGED test by moving the window with SDL_SetWindowPosition.
Owner save rule applies (runner exports NO_SAVE_WRITE).
