# NEXT: controller + display hot-plug (owner plays on a 65" TV with a pad; s7200 closed the audio side)
HYPOTHESIS-ID: input-display-hotplug
Context: src/main/main.cpp ~10883: SDL_CONTROLLERDEVICEADDED opens a pad only if none is open; REMOVED closes ours and
sets controller=nullptr. Read first (offline, no build): what the pad poll does with controller==nullptr (held buttons
latched? stick stuck off-centre?), and whether a SECOND connected pad is ever adopted after ours is removed (it is not
re-scanned: only an ADDED opens). Display side: grep SDL_WINDOWEVENT (~11938) for DISPLAY_CHANGED / fullscreen handling;
G1f item (3) "moving between displays" was "if feasible" and never measured.
Hypotheses:
- H-pad-latch: after REMOVED mid-hold the last button/stick state stays applied (craft keeps turning/firing).
- H-pad-orphan: with two pads, removing the open one leaves input dead though pad 2 is present.
- H-pad-ok: state clears and the next pad is adopted (then only the display side remains).
- H-display: fullscreen window on a display that goes away (TV off) stays on a dead display / wrong size; RESMULT and
  ASPECT=auto do not follow the new display.
Discriminator: forced arm ROGUESQ_PAD_REMOVE_TEST=<sec> pushing a synthetic SDL_CONTROLLERDEVICEREMOVED for the open pad
(the s7199 REMOVE_TEST pattern), logging the per-frame pad word sent to the guest before/after. Real-device positive
control if a pad is connected (check `SDL_NumJoysticks` log line); otherwise the synthetic arm plus a code-read. Display:
a CGVirtualDisplay (private API, tools/) create/destroy if it works unsigned; else code-read + SDL_WINDOWEVENT log only.
Build all arms in one build (rule 13). Owner save rule applies (runner exports NO_SAVE_WRITE).
