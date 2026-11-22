# NEXT (s7823)
HYPOTHESIS-ID: g3-det-menu-pair
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7822 closed SELECT LEVEL + level description (element match 1.000, ctl 0, plant 0). Unchecked front end after it: START on
SELECT LEVEL -> craft select (AVAILABLE CRAFT) -> START -> mission briefing / load screen.
Unit: one VI-clocked rdplog pair (NO RS64_RDP_BIN_WIDTH):
  env PCLOCK=vi AP0=6:start,11:start,11.5:w1024 OFF=5.75 PP=19.5:start,31.5:start,43.5:start,55.5:right,67.5:start ND=2 RSECS=100 PSECS=90 \
    VIDEO=tools/oracle/rdplog/rdplog.dylib RENV="RS64_RDP_BIN=$PWD/scratch/s7823/retail.bin RS64_RDP_LOG=/dev/null RS64_RDP_BIN_MAX_MB=3000" \
    XE="RS64_RDP_BIN_PORT=$PWD/scratch/s7823/port.bin RS64_RDP_BIN_PORT_MAX_MB=3000" zsh tools/g3_menu_pair.sh scratch/s7823/rdp
  Locate sub-screens with a texrect/tri band timeline (s7822 entry method), confirm screen names from port windows
  (scratch/s7823/rdp/port/w_*.png), then per sub-screen:
  `python3 tools/s7821_rdp_screen_segments.py scratch/s7823/retail.bin scratch/s7823/port.bin --windows r0:r1,p0:p1,c0:c1`
  (control window = a different sub-screen whose static set differs). zstd the .bin files after scoring.
Hypotheses: H-match (non-strip elements ~1.0, ctl low, plant 0) / H-port (non-strip misses that are not scale strips: name the
draw) / H-route (arms on different screens: fix press timing; retail screen loads are 2-5 s slower).
