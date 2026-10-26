# G1e step 4b: FPS60 audio sync + hangar/title
HYPOTHESIS-ID: g1e-framerate
Hypotheses: H-clean (FPS60 only changes gfx task rate); H-audio (dialogue/music cue scheduling counts frames -> desync at FPS60); H-menu (hangar/title fades count frames).
lvl10 snap soak (s6257) folded in s6258: no new frame-locked words (weak: int arm had no control).
Unit: (2) with ROGUESQ_FPS60=1 vs unset, one run each on a level with scripted dialogue: wall-clock from mission start to first N dialogue/music cue events; ratio ~1 -> H-clean, ~0.5 -> H-audio. (3) Title->hangar with FPS60=1: VI-origin-change timestamps vs retail; ~0.5 -> H-menu (lever only rewrites byte 0x80128EAF when ==2, i.e. flight; confirm). Build both arms and queue as soaks.
