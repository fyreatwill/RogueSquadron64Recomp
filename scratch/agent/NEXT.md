# NEXT (s7820)
HYPOTHESIS-ID: g3-det-menu-pair
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7819 made every retail-vs-port pair tool deterministic and owner-save-safe. Past G3 menu verdicts (s6783-s6800) were taken
against a wall-clock retail oracle whose frames jitter run to run, so their residuals mixed oracle noise with port defects.
Unit: re-run one front-end route (title -> SELECT GAME -> SELECT LEVEL -> hangar) with tools/g3_menu_pair.sh twice, score port
vs retail with tools/g3_rdp_frame_match.py (or g3_oracle_match.py --win, s6741 geometry --h 336 --win 124,964 --winx 0,1280).
Hypotheses: H-noise (old residuals were oracle jitter: det retail shrinks them, port vs retail matches within 1 run-to-run port
spread) / H-port (a stable per-screen residual remains in both runs at the same spot: name the screen and the draw) /
H-timing (residual tracks press timing offset OFF=7.3 only). Discriminator: per-screen residual in r1 and r2 vs the r1-r2 port spread.
Positive control: paint one block into a port capture and it must score as a residual.
