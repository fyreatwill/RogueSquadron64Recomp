# NEXT (s7826)
HYPOTHESIS-ID: g3-det-menu-pair
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7825 closed the logo quarter-pixel residual (input timing, not FPU; tools/s7825_tri_shift_bias.py). Resume the det pair at
the first mission frames: one more START after the Chapter I crawl (crawl was exact 120/120 in s7824).
Unit: one VI-clocked rdplog pair, s7824 route + one extra START ~12 s after the crawl starts (retail crawl starts ~800 frames
later than port; give retail RSECS +20):
  env PCLOCK=vi AP0=6:start,11:start,11.5:w1024 OFF=5.75 PP=19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start,103.5:start ND=2 RSECS=150 PSECS=135 \
    VIDEO=tools/oracle/rdplog/rdplog.dylib RENV="RS64_RDP_BIN=$PWD/scratch/s7826/retail.bin RS64_RDP_LOG=/dev/null RS64_RDP_BIN_MAX_MB=6000" \
    XE="RS64_RDP_BIN_PORT=$PWD/scratch/s7826/port.bin RS64_RDP_BIN_PORT_MAX_MB=6000" zsh tools/g3_menu_pair.sh scratch/s7826/rdp
  Check the retail press list the launcher prints actually reaches past the crawl (s7824 retail: 97.25 was the crawl START).
  Band timeline via scratch/s7824/tl.py (edit paths), screen names from port windows, then per screen
  `python3 tools/s7821_rdp_screen_segments.py R P --windows r0:r1,p0:p1,c0:c1 --tri-geom`; on any quarter-pixel tri residual run
  `python3 tools/s7825_tri_shift_bias.py R P --win r0:r1 --off o0:o1 --controls` (0.5 = noise, one-signed + size-scaled = input).
  Mission frames are 3D and time-animated: expect the s7821 rate split; score elements (HUD texrects) not whole frames.
  zstd the .bin files after scoring (rs64_zopen reads them).
Hypotheses: H-match (HUD/texrect elements ~1.0, tri residual explained by rate/timing) / H-port (an unexplained element miss: name
the draw) / H-route (the extra START lands elsewhere in retail: loads are slower, widen spacing). If the mission load leaves the
menu ucode, confirm the retail rdplog still records it (count frames after the crawl in both arms).
