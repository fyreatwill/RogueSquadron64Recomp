# NEXT: fold s6427_aspect_menufix soak
HYPOTHESIS-ID: g1d-widescreen
s6427 change: tools/apply_s6031_far.py no longer W/512-scales 320-wide cameras (attribution/N64 logo cams were scaled w 320->497 cx 160->248 into an unwidened 320/640 fb; logo drawn +78 px right in a169 w640 dumps, see /tmp-free ref scratch/agent/m6/g1_lvl1s6425_a169/fbd/fb_0000303_w640.ppm vs a43ref).
Next: fold SOAK-RESULTS line, compare fb_0000303 in g1_lvl1s6427_a169 vs a43ref (logo centred => H-320cam confirmed; still shifted => the 640x480 logo cam is the culprit: its [vpw] line is suppressed by nl6112<12 log budget, log first sight of each cam). Then 16:9 radar clip, menu stride garble (w640 later frames), hangar 21:9, G1e.
