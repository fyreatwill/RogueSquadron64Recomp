# NEXT: ROGUESQ_HANGAR_FOV under ROGUESQ_FPS60 (the owner's G3f run recipe)
HYPOTHESIS-ID: hangar-fov-optin

Context: s6836 landed the knob (4:3), s6837 verified it with ASPECT 16:9/21:9 (H-ok). The owner's fish-eye report came from an
FPS60 run; FPS60 splits frames at 60 Hz and s6791 saw the same delta-time pan curve at 60 Hz, but the knob was never run there.
Hypotheses: H-ok (fovy 38 on every 800cd670 call at ~2x call rate, pan path = FPS60 plain arm) vs H-split (an FPS60 interpolated
or duplicated camera call path reaches guPerspective without the setupCameraMatrices patch, so alternate frames show 45 ->
lens flicker).
Run: copy scratch/s6837/arms.sh to scratch/s6838/arms.sh, arms "ROGUESQ_FPS60=1" and "ROGUESQ_FPS60=1 ROGUESQ_HANGAR_FOV=38"
(+ optionally one ASPECT=21:9 FPS60 knob arm), ROGUESQ_G3F_CAM in all.
Discriminator: G3F per-cam table: all 800cd670 calls f38 in the knob arm (any f45 on 800cd670 = H-split), call count ~2x the
s6836 30 Hz arm; plus a BURST=40,48 window grab to check consecutive frames for lens flicker (ship size alternating).
H-ok -> add "works with FPS60" to OWNER-OPT-INS and close the thread (owner picks the value). Then the next 3c ladder rung with
an open item; remaining owner judgements: FPS60 feel, G1d/G3c sheets, hangar FOV value.
