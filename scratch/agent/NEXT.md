# NEXT: G3 render fidelity -- the phase after the opening crawl (mission intro / first Mos Eisley flight) vs retail
HYPOTHESIS-ID: g3-mission-intro-oracle-diff

s6738-s6742: boot cinematic, attract flight, cinematic replay, 4:3 hangar and the opening crawl (640x300 @0x6A2900, s6742)
are H-match vs retail (angrylion). Next: what the game shows after the crawl ends (retail crawl started at 79.7 s and was
still running at 110 s).
Hypotheses: H-match, H-rt64 (port draws differently on the same RDP stream), H-geom (missing/extra objects),
H-pos (camera/time differs -> compare only min-d matched frames; scripted mission-start cameras should match).
Steps:
1. Retail: env PRESS=6:start,...,56:start,61:start SECS=200 ARM=115 RD=retail2 zsh scratch/s6742/retail_brief.sh, but first
   change the dump width to the post-crawl width (unknown: run once with --vi-trace only, SECS=200, and read the WIDTH
   transitions after 110 s; mission flight was 512 wide in s6739). Do NOT press Start during the crawl (it may skip it;
   that would also be a cheap way to reach the mission faster -- test it in the trace run with a press at 90 s).
2. Port: SAVE_FROM=<oracle .eep> AP=6:start,...,41:start SECS=<match> CAP0=<crawl end> tools/g3_port_capture.sh
   scratch/s6743/port1 (port crawl starts 59.9 s, ~20 s earlier than retail). Measure the picture box (s6742: 640x300 -> rows
   244..844; 512x336 -> 124..964).
3. tools/g3_oracle_match.py <oracle.log> <portdir> <out> --w <W> --bases <origin-0x500,...> --h <rows> --win y0,y1
   Control: same-run median over other port frames, plus a wrong-box --win run.
