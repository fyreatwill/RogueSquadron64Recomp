# NEXT: G3 -- mission-2 intro cinematic runs 25.2-26.2 s retail vs 22.2-22.3 s port
HYPOTHESIS-ID: g3-lvl2-intro-duration

s6748: mission 2 (Barkhesh) flight + bolts H-match vs retail angrylion. Same save in both arms: scratch/s6748/lvl2.eep
(tools/g3_eep_patch.py, oracle save with selected mission 1, re-signed). But the 640 intro phase (no input in any arm) took
26.2/25.2 s retail (scratch/s6748/recon, retail_bz: 640 at 79.7/80.6 s, 512 at 105.9/105.8 s) vs 22.3/22.2 s port
(port3/port_bz: 640 at 42.6 s, 512 at 64.9/64.8 s). lvl1's intro matched (s6743 16.5 vs 16.3 s).
Hypotheses:
- H-load: retail spends ~4 s loading/decompressing before the cinematic plays (initial retail 640 frames black/static with
  no port match), then port and retail run at the same rate (constant offset). Expected port property, not a defect.
- H-cine-rate: the cinematic plays slower in retail; the retail-port offset grows steadily through the phase.
- H-skip: a shot/segment present in retail is missing or shortened in the port (a run of retail frames with no port match).
- H-tail: the extra time is at the end (fade/hold before flight; last retail frames match the last port frame).
Steps (one game at a time):
1. Retail: env RD=intro ARM=60 NDUMP=60 D0=0 DT=0.5 SECS=115 zsh scratch/s6748/retail.sh, but with 640-wide dumps:
   copy retail.sh's dump loop with `--fb-dump 640:$d:...` (s6743 used --bases 695C00,62B800 --h 336; the mission-2 640 origin
   is 0x696100/0x696600, so read the bases from the [fb-dump] origin0 values) and --fb-arm-after 70 so it arms on the intro.
2. Port: env PD=intro AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start SECS=70 CAP0=40
   zsh scratch/s6748/port.sh (window rows: re-read the letterbox geometry from a capture).
3. g3_oracle_match.py with the 640 geometry; plot retail t vs matched port t. Initial unmatched block + constant offset =
   H-load; linear drift = H-cine-rate; a mid gap = H-skip; extra retail frames at the end matching the last port frame = H-tail.
Owner save must be restored and sha-verified (scratch/s6748/owner_save.sha); mupen .eep must be cmp-equal to
scratch/s6747/oracle.eep afterwards.
