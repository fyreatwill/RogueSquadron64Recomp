# NEXT (s7228): why the HOTPLUG=0 path pins at a flat 30/s after a display move, and does a WINDOWED move do it on the default path
HYPOTHESIS-ID: display-move-present-rate
Context: s7227 (scratch/s7227/arm.zsh, ring_fix/ring_old): after the target display was removed while fullscreen, the default path
(s7202 cycle) presents 30-60/s on screen; HOTPLUG=0 (macOS moves the window alone, one swap chain step 1512x949) is a flat 30/s for
52 s and never logs `layer drawable 3024x1898 != swapchain` (RT64 1x chain into a 2x layer). The owner path is the default, so this
matters only if a WINDOWED move between displays (drag, or windowed removal; no fullscreen cycle runs there) also pins at 30.
Hypotheses: H-scale (1x chain in a 2x layer forces a compositor scale pass -> half rate; layer-drawable resize fixes it),
H-space (macOS-moved fullscreen window is not direct-to-display; windowed unaffected), H-content (phase: old arm happened to sit in a
30/s flight stretch - refuted if pre-removal 60 bursts in the same run recur at the same route time).
Run (one build, current binary, 2 arms sequential): scratch/s7227/arm.zsh variant with ROGUESQ_FULLSCREEN=0 (windowed on display 1,
removal at ~172 s, no toggles) default vs HOTPLUG=0; score on-screen P/s after removal (python in s7227 ledger entry: P rows with
at>0 after the first w=1512 Z row) and [g1f-win] layer rows.
Outcomes: windowed default 30-60 & old flat 30 -> H-scale (the layer resize is what matters; already default on); both 30-60 ->
H-space, fullscreen-only, close as covered by the default; both flat 30 -> new defect on the windowed path, fix.
