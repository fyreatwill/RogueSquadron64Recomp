# NEXT (s7824)
HYPOTHESIS-ID: g3-det-menu-pair
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7823 closed AVAILABLE CRAFT + SELECT YOUR CRAFT (SYC whole frames exact 115/120). Unchecked front end after it: START on
SELECT YOUR CRAFT -> mission briefing / text / load screen -> first mission frames.
Unit: one VI-clocked rdplog pair (NO RS64_RDP_BIN_WIDTH), s7823 route + START at 79.5 and 91.5 (drop the useless right press):
  env PCLOCK=vi AP0=6:start,11:start,11.5:w1024 OFF=5.75 PP=19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start ND=2 RSECS=125 PSECS=115 \
    VIDEO=tools/oracle/rdplog/rdplog.dylib RENV="RS64_RDP_BIN=$PWD/scratch/s7824/retail.bin RS64_RDP_LOG=/dev/null RS64_RDP_BIN_MAX_MB=4000" \
    XE="RS64_RDP_BIN_PORT=$PWD/scratch/s7824/port.bin RS64_RDP_BIN_PORT_MAX_MB=4000" zsh tools/g3_menu_pair.sh scratch/s7824/rdp
  Band timeline: reuse scratch/s7823/tl.py (change paths; it pickles frames), confirm screen names from port windows
  (scratch/s7824/rdp/port/w_*.png contact sheet), then per new screen:
  `python3 tools/s7821_rdp_screen_segments.py R.bin P.bin --windows r0:r1,p0:p1,c0:c1 [--strip-w 54:69] [--screen p0:p1]`.
  If the mission load leaves the menu ucode/width (port phase ordinal changes), check the retail rdplog still records it.
  zstd the .bin files after scoring.
Hypotheses: H-match (non-strip elements ~1.0, misses scale-explained, ctl low, plant 0) / H-port (unexplained non-strip miss:
name the draw) / H-route (arms on different screens: retail loads are 2-5 s slower, widen press spacing).
