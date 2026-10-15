# Next work unit
HYPOTHESIS-ID: keyed-mission-image-vs-silent-ab
s4964_mission_image and s4964_mission_silent are enqueued (s4965). Unit: read the two new SOAK-RESULTS.md lines (logs in scratch/agent/soak_results/s4964_mission_{image,silent}/), compare onset t, crash/abort, vi_origin_rows. Controls: silent pcm_nz_rows=0, image >0 (else arm invalid, re-enqueue).
H-stable-both: audio not the mission stability factor. H-image-regresses: image crashes/stalls, silent not. H-silent-regresses: silent crashes.
If a recipe did not run, check soak_queue/ and the loop log before re-enqueuing.
