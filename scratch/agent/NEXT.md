# NEXT (s7822)
HYPOTHESIS-ID: g3-det-menu-pair
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7821 closed title -> SELECT GAME (panel) -> hangar at RDP level (no port defect). The hangar's sub-screens are unchecked:
LEVEL DESCRIPTION (C-button in the hangar), craft scroll (right), and the mission briefing / load after START on a craft.
Unit: one VI-clocked rdplog pair (NO RS64_RDP_BIN_WIDTH: the route crosses widths), e.g.
  env PCLOCK=vi AP0=6:start,11:start,11.5:w1024 OFF=5.75 PP=19.5:start,31.5:start,43.5:cup,55.5:cup,63.5:right ND=2 RSECS=95 PSECS=85 \
    VIDEO=tools/oracle/rdplog/rdplog.dylib RENV="RS64_RDP_BIN=$PWD/scratch/s7822/retail.bin RS64_RDP_LOG=/dev/null RS64_RDP_BIN_MAX_MB=3000" \
    XE="RS64_RDP_BIN_PORT=$PWD/scratch/s7822/port.bin RS64_RDP_BIN_PORT_MAX_MB=3000" zsh tools/g3_menu_pair.sh scratch/s7822/rdp
  (check the C-button key name in g3_menu_pair's mapping / rs64_oracle --press first; retail hangar entry is ~8 s after the press
  on SELECT GAME; leave >= 10 s between presses). Score: `python3 tools/s7821_rdp_screen_segments.py retail.bin port.bin` for
  static screens, `--elements <retail width>:<port phase> --ctl-phase <other>` for animated ones (hangar runs ~16 fps retail vs
  30 port, so whole frames never pair there).
Hypotheses: H-match (layout exact / element sets equal, residual = animation phase) / H-port (an element present in one arm
only, beyond scale-animated strips: name the draw) / H-route (arms on different sub-screens: fix press timing first).
Positive controls: worst-pair segment control and the +0.25 px plant in --elements must read ~0.
