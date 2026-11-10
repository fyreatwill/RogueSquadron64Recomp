# NEXT: FPS60 near-wall flicker: same-run split, then name the camera term (owner reports first)
HYPOTHESIS-ID: fps60-wall-camera
Context (s7098): the large in-flight terrain drops RT64 presents are already in the RDP stream (angrylion paints the same hole).
They are the near canyon wall vanishing for 1-3 frames while the camera hugs or enters it. Cross-run, single runs, L6: dd4 FPS60
6/4 episodes, dd4 FPS60=0 0 episodes (130 s wall-hug), dd1 FPS60 2. CULL_SPIKE=tog refuted the cull. FPS60 = events.cpp g1e::apply
clamps arbiter byte 0x80128EAF 2->1, so the game sim itself runs a tick per VI with dt 1/60.
Hypotheses:
 H-osc   the camera's terrain push-out / follow spring is tuned for dt 1/30; at 1/60 it overshoots, so the eye alternates between
         the outside and inside of the wall surface (frames alternate wall / no wall, as in the t6 52.4 s burst and the d6 rows)
 H-par   a camera or terrain-collision routine runs on frame-counter parity (every 2nd tick); at 60 Hz half the frames skip it
 H-ret   retail at 30 Hz also puts the eye inside the wall; 60 Hz only doubles how often it shows (then the rate per sim tick is equal)
Unit (ONE run, same-run split, no FPS60 env):
 1. L6 dd4 16:9, ROGUESQ_FPS60=0 ROGUESQ_G1E_LIMIT=1 ROGUESQ_G1E_WIN=600 (60 fps in alternate 10 s windows; [g1e] lines give the
    window edges), plus a per-VI guest-RAM log of the camera eye (find it: s6876 camera pitch rows, tools/fixup_fps60_deadband.py
    notes) and the player position 0x80137DBC rec+0..8. Use scratch/s7098/arm.zsh (edit the FPS60=1 out of XENV_EXTRA for this arm)
    with g5b_capture, then `python3 tools/s7098_wall_flicker.py <raw> <csv>` split by window parity.
 2. Positive control: the wall-flicker detector must find >=1 episode in the 60 fps windows (it found 2-6 per run before).
Outcomes: episodes only in 60 fps windows + eye-to-wall distance sign alternating per tick = H-osc; eye update missing on alternate
ticks = H-par; equal episodes per sim tick in both = H-ret (then report it to the owner as retail). Fix only after the term is named.
Tools: tools/angrylion_replay/build16.sh (16 MB core: the stock one SIGSEGVs on dd>1 frames), tools/s7098_rt64_vs_al.py,
tools/s7098_transients.py.
