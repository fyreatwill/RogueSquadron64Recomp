# NEXT: G3 cinematic sweep via AT THE MOVIES
HYPOTHESIS-ID: g3-cinematic-sweep

Done s6791: G3f closed as retail. The craft-select camera slides sideways in ~0.5 s with yaw lagging ~3 s, under a fixed 45 deg /
1.882 projection, identical in retail and in FPS60 on and off. The owner may want an opt-in hangar FOV knob; build it only if asked.

Work unit (CURRENT-TRUTH Next steps 1): the MAESTRO+DIRECTOR passcode route plays every cutscene back to back. Match each cutscene
against retail (scratch/s6787/tools/cine.py + align.py), including ending cutscenes that are otherwise unreachable. The port dump needs
PMAX_MB; retail needs RBW=all.
Hypotheses per cutscene: H-match (port = retail within control spread), H-render (a fixed per-cutscene pixel/RDP difference),
H-timing (same frames, different phase/duration). Discriminator: per-cutscene aligned frame distance vs a same-run cross-cutscene
control; a cutscene above the control floor is a datum to root-cause.
Owner opt-ins that stay unverified: AT THE MOVIES with FPS60.
