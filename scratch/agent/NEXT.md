# NEXT (s7819)
HYPOTHESIS-ID: port-capture-private-save
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7818 made `--det` the oracle default in the retail-only launchers, but tools/g3_{menu,showroom,ai_gap}_pair.sh could not be
converted: their port arm is tools/g3_port_capture.sh SAVE_FROM, which copies an .eep over build/saves/rs64.n64.us.1.0.bin (the
owner's real save) and restores it on exit. The owner save rule bans that, so every retail-vs-port pair tool is unusable.
Unit (bounded change):
 1. g3_port_capture.sh SAVE_FROM: build a private game dir under OUTDIR (symlink or copy build/RogueSquadron64Recomp + the ROM +
    whatever data the binary reads relative to cwd; own saves/ holding the SAVE_FROM eep) and run from it via the existing
    GAMEDIR path; never touch build/saves. Remove the backup/trap swap.
 2. Positive controls in the same session: (a) `shasum build/saves/*` before == after a SAVE_FROM run; (b) the port shows the
    SAVE_FROM save's level, not the owner's (s6741: owner save selects THE JADE MOON, lvl1.eep selects AMBUSH AT MOS EISLEY) ->
    read the level name from a window capture or the [phase]/save log line; (c) a control run with the owner save (no SAVE_FROM)
    still shows THE JADE MOON.
 3. Then splice `$ODET` into the three pair scripts' oracle command and run one (g3_menu_pair.sh with its documented PP) twice:
    retail dumps byte-identical across the two runs (tools/s7817_oracle_det.py).
Hypotheses for (1): H-cwd (the binary reads saves/ and the ROM relative to cwd: a private dir works as is) / H-abs (it resolves a
fixed data path, e.g. ~/Library/...: needs an env override) / H-assets (other cwd-relative files needed: copy fails until listed).
Screen must be unlocked (the script exits 4 when locked); one game run at a time; CPU rule max 2 heavy jobs.
