# NEXT: SHOWROOM > AT THE MOVIES + Concert Hall track change (G3)
HYPOTHESIS-ID: g3-showroom-movies

Done s6786: MAESTRO -> OPTIONS > SHOWROOM (screen 10) and CONCERT HALL match retail at RDP level (texrect sets identical;
3D tri gap = RNG ship/pose); song worker runtime H-disjoint in both arms.
Last undriven front-end items: SHOWROOM > AT THE MOVIES (cinematic viewer?) and Concert Hall track changes (>>> = next song,
which should send a new song request through the song worker each time).
Unit (no build):
1. AT THE MOVIES: `env GAP=16 DWELL=60 EXTRA="12:down,15:a" zsh tools/g3_showroom_pair.sh scratch/s6787/mov`
   (check the port window captures for the cursor: SHOWROOM opens on CONCERT HALL). If it opens a movie list, add presses.
   Score tails with tools/g3_rdp_phase.py retail.bin port.bin; control = scratch/s6786/r4/port.bin (CONCERT HALL).
   If it plays an FMV/cinematic, the cinematic overlay (segment 0x137580) loads: also check overlay load + no crash.
2. Concert Hall tracks: `env GAP=16 DWELL=70 EXTRA="12:a,20:right,30:right,40:right,50:left" zsh tools/g3_showroom_pair.sh
   scratch/s6787/trk` and count 0x800C3B38/0x800C5880/0x800C3B54 rows per arm (expect one request per track change in both)
   and the track-title texrects per segment (ROGUE TITLE -> next names) in the same order.
Hypotheses: H-match (same screens, same per-change song request sequence) vs H-diff (name the writer: missing track
request, different title order, or a second request overtaking a completion = the s6781 race on the song path, since the
port's worker completes in the send tick and retail ~9 ticks later).
If AT THE MOVIES cannot be reached by schedule after 2 tries, close the front-end and take the next ladder rung (G1c
phase 2 draw distance or G1e frame rate, per ITERATION 3c).
