# NEXT: G1d step 33 - why does 21:9 (w1045) fail at 12 MB while 16:9 (w796) works
HYPOTHESIS-ID: g1d-widescreen
Known (s6140): 12 MB: 16:9 OK (dump w796 correct flight), 21:9 stuck (dump w320 stripes, VI origin alternates at width 1045, guest in s3294-stall). Harness MISSION_RE is invalid for wide arms: judge by fbd dump width/png.
Hypotheses: H-size (FB/pool size >~500 KB or total exceeds 12 MB pool -> try ROGUESQ_OSMEM_MB=16), H-width (a width-dependent constant e.g. 1024 cap/stride), H-aspect-math (21:9 projection value).
Discriminator, one script, sequential arms: 21:9 at OSMEM_MB=16; 16:9-like intermediate aspect (e.g. 18:9) at 12 MB; read dump widths. 16:9@12 is the positive control.
Then: HUD edge anchoring, menus/hangar at wide, bundle OSMEM default under ROGUESQ_ASPECT.
Note: macOS sed -i needs '' arg; write scripts via heredoc; copy scratch/agent/s6140_run.sh.
