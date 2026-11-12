# NEXT (s7222): RETINA=1 display ADDED while fullscreen on the 2x built-in (reverse of s7221)
HYPOTHESIS-ID: retina-hotplug
Context: s7221 closed removal (1x display removed while fullscreen -> re-enter on built-in at 3024x1898). Untested: a display
ADDED while the game is fullscreen on the built-in. The s7202 handler logs [g1f] on any display event; it should NOT leave
fullscreen or resize for an add.
Hypotheses: H-ok (no leave/re-enter, layer stays 3024x1898, on-screen presents continuous 30/s through the add); H-churn (the add
triggers the leave/re-enter path or a swap chain resize, a visible blink / gap >250 ms); H-dead (Space change hides the game, P at=0).
Run: copy scratch/s7221/arms.zsh, but start the game with NO window pos (built-in), FULLSCREEN=1 ASPECT=auto, sleep 20, THEN
start build/virtual_display 1920 1080 15 (add at ~20 s, removed at ~35 s), screencapture at +5 s after add and +5 s after removal.
Arms a1 RETINA=1, a0 RETINA=0. Score with scratch/s7221/sum.py (P at>0 per second from 15 s, Z rows), grep [g1f]/[g1f-win]/[retina].
Positive control: vd log ndisp 1->2->1 and [s7199-hotplug] added row in the log; on-screen P>0 before the add (built-in reports at).
Outcomes: H-ok -> retina-hotplug closed for good, move to backlog item 2+ (owner-look items: produce nothing new; take the next
ladder rung not closed, e.g. G1e/G3 checks at RETINA=1 21:9 window); H-churn -> gate the handler to removals of the window's display;
H-dead -> fix in rs64_display_hotplug_tick.
