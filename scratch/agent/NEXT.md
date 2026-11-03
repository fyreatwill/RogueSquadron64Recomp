# NEXT: abort-level transition frame (striped magenta/yellow terrain) — retail or port?
HYPOTHESIS-ID: g3-abort-transition-frame

Context: s6840 closed g3-hangar-artifacts (H-clean, tools/g3_band_scan.py). Side datum: s6798 21:9 capture
scratch/s6798/tog21/w133_166_77890.png (context sheet scratch/s6840/w21_w133_context.png) is the first frame after
PAUSE -> ABORT LEVEL -> YES: terrain drawn as magenta/yellow stripes, white sky, top ~40% black, X-wing normal.
The s6840 4:3 and 16:9 arms (same route, scratch/s6840/menus.sh, abort at AP 128:left,131:a) did not catch it, but
caps are ~0.6 s apart, so those misses are NOT nulls.

Hypotheses:
- H-retail: retail draws the same frame (terrain texture/TLUT already released while the last flight DL runs).
- H-port-tex: our RT64/LLE path samples a freed/reused texture or TLUT (stale TMEM upload, tile cache keyed on a
  recycled address) on the teardown frame.
- H-wide: only the wide FB/heap layout (s6631-class overlap) exposes it; 4:3 is clean.

Discriminator (one build, phase-gated on the ABORT press, not a stopwatch):
1. Port 4:3 and 21:9, same route, RS64_RDP_BIN_PORT=<f> RS64_RDP_BIN_PORT_VI=1 plus dense in-process window grabs
   (tools/g3_port_capture.sh BURST style / winctl burst) from the YES press to +3 s. Positive control: the striped frame
   must be findable by the magenta-pixel count (R>200,G<110,B>90, >150 of 160x90 — fired 914 on w133, 0 elsewhere).
2. Retail oracle (tools/oracle, rdplog plugin, --save-dir private save copy; scratch/s6799/retail_rdp.sh pattern) with
   the same press sequence; angrylion dumps around the abort.
Outcomes: retail shows it -> H-retail, close. Port 4:3+21:9 show it, retail not -> compare the TEXTURE/TLUT loads in
the RDP stream on that frame (tools/g3_rdp_frame_match.py) -> H-port-tex, name the writer. Only 21:9 -> H-wide.
Run one game at a time. Defaults stay retail.
