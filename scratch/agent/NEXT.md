# NEXT: G3 render fidelity -- first lvl1 (Ambush at Mos Eisley) flight frames with HUD vs retail, plus the brightness gain
HYPOTHESIS-ID: g3-mission-start-oracle-diff

s6738-s6743: boot cinematic, attract flight, cinematic replay, 4:3 hangar, opening crawl and the mission-intro cinematic
(640x336 @0x695C00/0x62B800) are H-match vs retail angrylion. Next: the in-mission 512 flight right after the intro.
Retail recipe (s6743 skip90): Start 6..61 s and 90 s -> flight 512 @0x690400/0x690800 at 112.6 s (buffers 0x690000 /
0x620000 per s6739, check origin0 in the log). Port: AP=6:start,...,41:start reaches flight at ~156 s; a Start during the
port crawl (e.g. AP+=,50:start) should skip to the intro the same way -- check it, saves ~100 s.
Hypotheses: H-match; H-rt64 (HUD/radar/reticle drawn differently); H-geom (missing/extra objects); H-pos (no input ->
both should fly the same scripted start for a few seconds; compare only the first ~5 s and min-d matched frames).
Steps:
1. Retail: copy scratch/s6743/retail_intro.sh, dumps width 512 (--fb-dump 512:...), ARM=110, SECS=125, 20 dumps 0.5 s apart.
2. Port: SAVE_FROM=<oracle .eep> AP=...,41:start,50:start SECS=<flight+15> CAP0=<flight-2> tools/g3_port_capture.sh
   scratch/s6744/port1. Measure the pillar box (s6739: --win 124,964 --winx <x0,x1> for 512x336? check row count).
3. tools/g3_oracle_match.py <log> <port> <out> --w 512 --bases 690000,620000 --h <rows> --win ... --winx ...
   Control: same-run median + wrong-box run. Also tabulate retail/port per-channel mean ratio on d<6 pairs (brightness
   gain 1.8-2.5% seen s6740/s6743; if it holds on the HUD's flat colours too, it is a global output gain, not shading).
