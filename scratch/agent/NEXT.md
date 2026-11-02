# NEXT: ENTER NAME RDP compare, then native hangar RDP match (G3)
HYPOTHESIS-ID: g3-enter-name

Done s6784: menu worker overlap H-disjoint (tools/menu_worker_reach.py); title menu, OPTIONS top, post-erase SELECT GAME
match retail at RDP level. Front-end screen left: ENTER NAME.
Unit (one pair run each, no build):
1. ENTER NAME: R=$PWD/scratch/s6785; env PP=17:start,35:down,38:a,44:down,50:a,56:down,62:a,68:a ND=2 RSECS=100 PSECS=80
   VIDEO=tools/oracle/rdplog/rdplog.dylib RENV="RS64_RDP_BIN=$R/name/retail.bin RS64_RDP_BIN_WIDTH=1024 RS64_RDP_LOG=/dev/null"
   XE="RS64_RDP_BIN_PORT=$R/name/port.bin" zsh tools/g3_menu_pair.sh scratch/s6785/name
   (s6784 route ends on SELECT GAME with slot 1 erased at ~65 s port; the extra 68:a picks it -> ENTER NAME). Check the
   port window captures show ENTER NAME before scoring; if retail lags, add +2-3 s to the retail offset (OFF).
   Score: tools/g3_rdp_frame_match.py name/retail.bin name/port.bin --ctl scratch/s6784/rdp_opts/port.bin.
2. Native 4:3 hangar: same pair runner style on the hangar route (tools/g3_mission/run.sh header / s6741), RDP tail on the
   hangar idle view.
Hypotheses: H-match (exact or median within phase classes: pulse colour, spinning-model tri count) vs H-diff (missing or
extra items: name the writer). Cross-screen control must stay ~0 exact.
After this: G3 front-end and hangar closed -> take the next ladder rung per ITERATION.md 3c.
