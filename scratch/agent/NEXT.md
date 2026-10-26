# Next: G3c owner visual report (arm table first)
HYPOTHESIS-ID: g3c-owner-visual
Owner priority (ITERATION.md G3c). Three defects: (a) jagged far-terrain edge, (b) knife spikes (reopen: H-rsp-emu vs H-retail), (c) turn shake. Start with (c): cheapest single instrument - per presented frame log camera yaw/pos + craft yaw from guest RAM + present timestamp during a scripted steady turn; arms retail / FPS60 / ASPECT / both; shake = sign-alternating second difference retail lacks. Batch (a) into the same build: an arm table of which opt-ins show the terrain edge (retail control first, framebuffer dumps).
Parked (small): dd3 - tag grow sites by constant in tools/apply_s6098_dlpool.py (ra is always 0) to name the crashing site; s6289 showed the finder-grow never fires.
