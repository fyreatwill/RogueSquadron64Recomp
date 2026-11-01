# NEXT: G3 render fidelity -- same-camera in-flight diff on the ATTRACT DEMO (no input on either side)
HYPOTHESIS-ID: g3-attract-oracle-diff

s6738: boot intro cinematic = H-match vs retail after the LLE-default fix (LLE_FORCE/UNGATED/SOLO now default ON).
The port's title idles into an attract demo (scripted Tatooine flight, seen at t~74 s in scratch/s6738/fix_c2). The
demo is input-free, so retail and port should show the same camera: a real in-flight pixel diff.
Hypotheses: H-match (best-match d < ~5 lum on slow-camera frames, no clustered hot tiles); H-geom (tiles > 40 clustered on
objects/terrain present on one side only); H-shade (smooth per-channel offset / fog-haze difference across the frame);
H-desync (the demo diverges: best-match port time NOT monotonic in retail VI -> demo not deterministic, fall back to
element-class check and say so).
Steps (one retail run + one port run, then offline):
1. Retail: copy tools/g3_boot_diff/retail_boot.sh; SECS=110; fb-dumps armed on the first 512-wide VI (the demo; boot has
   no 512 phase: 320 -> 640 -> 1024 title at t=49 s), delays 0.5..35 s step 0.4, region 0x600000 len 0x200000 may not
   hold the flight buffers: first run with --vi-trace only to read the 512-phase origins (s5978 flight used 0x690400/
   0x690800 -> dump 0x680000 len 0x100000), keep `--press 999:start` so a controller is attached.
2. Port: env SECS=130 zsh tools/g3_boot_diff/port_win.sh attract1 (plain launch, window captures ~5/s).
   Find the 512-wide window crop (4:3 512x440-ish VI in a 640x480 window: measure non-black rows) for --win.
3. python3 tools/g3_oracle_match.py <oracle.log> scratch/s6738/attract1 <out> --bases <flight bases> --h <rows> --win y0,y1
   (decoder is hardwired W=640: add a --w option for 512). Inspect top pairs + heat maps.
Control: the static-title frame (1024 phase) should match too, or the method failed.
