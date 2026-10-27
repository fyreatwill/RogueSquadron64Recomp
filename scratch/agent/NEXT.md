# NEXT: G1d recheck after s6428 camera-scale fix
HYPOTHESIS-ID: g1d-widescreen
Queue ONE soak (copy scratch/agent/s6428_cam.sh pattern / s6427 soak): a43ref, a43, a169, a219 with hangar route; compare logo centring at 21:9, flight HUD/radar edges at 16:9 and 21:9, and check whether the noisy lower half of late w640 dumps is a dump-stride mislabel (dump tool uses 640 while vsu width is 796) - positive control: same dump in a43 arm should be clean.
Hypotheses: H-dumpmislabel (noise only in dumps, game output fine) vs H-menu-stride (real menu fb stride garble at wide aspect). Discriminator: dump w796 re-read of the same buffer.
Then G1e (frame rate measure) if G1d judged done by owner contact sheets.
