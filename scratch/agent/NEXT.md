# NEXT (s7760)
HYPOTHESIS-ID: rdp-output-gate-menu-overlays
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7759 closed the hangar re-entry path (AVAILABLE CRAFT H-state invisible 3/3, SELECT YOUR CRAFT 20/20 exact). Remaining unscored
screens on the owner route: the in-mission PAUSE menu (drawn over the frozen flight frame), ABORT LEVEL confirm, MISSION FAILED medal
and SELECT LEVEL. Overlays over a held frame are the likeliest place for a task to read RAM the CPU rewrites (fb-as-texture, menu DL).
Unit (one game run, screen unlocked, host idle): same command as s7759 (see its PORTING-STATE entry; scratch/s6995/route_long.txt,
owner save read-only via empty FORCE_*), with EVERY=60:24:10900 SECS=230 so snaps land VI 10900-12280 (~179-202 s: pause 182 s,
abort 188-193 s, medal 203 s; 60.8 VI/s, check against the 10 s window sheet). Then `python3 tools/s7757_route_replay.py <snapdir>`
and, per DIFF, `python3 tools/s7755_hstate_visibility.py <snap> --cap 1048576 --tg 1`.
Hypotheses: H-exact (overlay tasks replay byte-exact: add 1-2 to s7753 SNAPS) / H-state (begin != end but live==end <=1 LSB: add a
pair to s7756 PAIRS, name the RAM region) / H-overlay-race (live-vs-end ge2LSB > 0: a visible mid-task rewrite; name the writer).
Max 2 CPU-heavy jobs. If this also comes back exact/invisible, RDP-output route coverage is complete: take the next owner item or
G-rung per ITERATION 3c instead of more coverage.
