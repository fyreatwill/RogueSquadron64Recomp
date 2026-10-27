# NEXT: G1d wide-edge terrain holes, then G1e frame rate
HYPOTHESIS-ID: g1d-widescreen
s6431: wide-arm harness false negative fixed (use MISSION_WIDTH=796|1024 in wide recipes). Owner sheet built (scratch/agent/m6/s6429_view/owner_sheet_43_169_219.png).
Open datum: 16:9 flat sky-blue rectangle near terrain edge, 21:9 terrain hole left-centre. Work unit: count in fbd dumps (a169/a219, w796/w1024 frames) how many frames show such holes; H-cull (terrain cell footprint / frustum x-widening excludes cells at the edge), H-pool (dd1 pool too small for wide footprint), H-retail (4:3 control shows same). Compare same frames to a43 control; then G1e (distinct framebuffers/sec per level).
