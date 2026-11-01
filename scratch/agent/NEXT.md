# NEXT: G3 render fidelity -- retail briefing fly-over (640 phase after the hangar) vs port window captures
HYPOTHESIS-ID: g3-briefing-oracle-diff

s6738-s6741: boot cinematic, attract flight, cinematic replay and the 4:3 hangar are H-match vs retail (angrylion).
Hypotheses: H-match, H-rt64 (port draws differently on the same RDP stream), H-geom (missing/extra objects),
H-pos (camera/time differs -> compare only min-d matched frames; the fly-over is a scripted camera, so it should match).
Steps:
1. Retail: copy scratch/s6741/retail_hangar.sh, PRESS through ~51 s (README: pressing past ~58 s leaves the hangar into
   640 at 0x6a2900; a Start in the hangar selects the level). Dumps: --fb-dump 640:<d>:600000:200000 for d 1..30 s.
   Check the [vi] trace for the 640 origins and derive bases (origin - 0x500).
2. Port: SAVE_FROM="$HOME/Library/Application Support/Mupen64Plus/save/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep"
   AP=6:start,11:start,16:start,21:start,28:start SECS=80 CAP0=28 tools/g3_port_capture.sh scratch/s6742/port1
   (port hangar at 23.9 s; s6741 port1 left it to 0x6A2900 at 42.5 s with presses to 41 s). Measure the 640 picture box.
3. tools/g3_oracle_match.py <oracle.log> <portdir> <out> --w 640 --bases <..> --h <rows> --win y0,y1
   Control: a frame from a different phase (hangar captures) must score far worse, as s6741's Jade Moon control did.
