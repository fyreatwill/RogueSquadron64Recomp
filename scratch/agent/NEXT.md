# NEXT (s7592)
HYPOTHESIS-ID: thread-creation-census

Class MR closed s7591 (12 rows, one gated uref leak fixed, ROGUESQ_S7591_HOSTPORT=0 = old). Class TH = thread / timer creation
sites in OUR code (src/, lib/N64ModernRuntime, lib/rt64/src incl. plume; not SDL/system): every std::thread, pthread_create,
SDL_CreateThread, dispatch_source_create, dispatch_async onto a new queue, NSTimer/CFRunLoopTimer. Classify per site:
  joined (handle kept and joined/stopped at shutdown or re-init) | detached-once (started once per process) |
  per-event (started per load / resize / fullscreen toggle / menu: is the old one stopped first?) | gated (diagnostic env only).
s7589 measured threads flat over the hangar route, but resize, fullscreen toggle, aspect switch and options menus were never
exercised; a per-event row that starts a thread without stopping the previous one would grow there.
Hypotheses: H-clean (no unbounded per-event row), H-gated (only gated rows grow), H-event (a default per-event row grows: fix it,
env =0 old).
Tool: tools/s7592_th_census.py --controls (plant file with a joined, a detached-once in a static init, and a per-event leak).
Runtime witness for any per-event row found: tools/s7589_hrsample.zsh thread count across N repetitions of that event
(e.g. fullscreen toggles via the key the owner uses), plant = a gated dummy thread per event.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
