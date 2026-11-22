# NEXT (s7821)
HYPOTHESIS-ID: g3-det-menu-pair
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7820 closed title -> SELECT GAME (no port render defect; backdrop photo = rand timing; RDP texrect layout exact 102/103).
The rest of the front-end route (SELECT LEVEL, hangar/craft select) has not been re-checked against the deterministic oracle.
Unit: one VI-clocked rdplog pair that reaches SELECT LEVEL and the hangar, e.g.
  env PCLOCK=vi AP0=6:start,11:start,11.5:w1024 OFF=5.75 PP=19.5:start,25.5:start,31.5:start ND=2 RSECS=60 PSECS=50 \
    VIDEO=tools/oracle/rdplog/rdplog.dylib RENV="RS64_RDP_BIN=$PWD/scratch/s7821/retail.bin RS64_RDP_BIN_WIDTH=1024 RS64_RDP_LOG=/dev/null" \
    XE="RS64_RDP_BIN_PORT=$PWD/scratch/s7821/port.bin" zsh tools/g3_menu_pair.sh scratch/s7821/rdp
  (check presses land: retail screen loads are slower; leave >= 6 s between presses), then
  python3 tools/g3_rdp_frame_match.py retail.bin port.bin --ctl <a title-only port bin> --k 120, plus the s7820 decomposition
  (texrect geometry / geometry-without-PRIM, see PORTING-STATE s7820) per screen. Pixel pass: g3_oracle_match.py with
  `--w 512 --h 448 --bases 790000 --win 66,1024 --winx 86,1194 --dec shift` (512x448 screens; check the origin/width per screen).
Hypotheses: H-match (texrect layout exact, residual = PRIM/animation phase) / H-port (a texrect or tri set present in one arm
only at the same screen in both runs: name the screen and the draw) / H-route (presses diverge, the arms are on different
screens: fix offsets first). Positive control: title-only port bin as --ctl (must not match), planted block for pixels.
