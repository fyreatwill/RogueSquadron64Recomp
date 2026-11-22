# NEXT (s7835)
HYPOTHESIS-ID: g3-port-halftick-dt
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: s7834 closed the flight-pitch thread. Port and retail CPO1 are bit-identical (460 words, player + camera) for the first two lvl2
flight frames; at frame 2 (port ramdump n=840) the port's player advances 0.5 tick where retail advances 1, and the camera swing-in
settles at another pitch. Sub-pixel and not owner-visible, so this is LOW value: ONE unit only, then close single-source either way.
Question: where does the port's half-tick dt come from?
Hypotheses:
 - H-count: the game's elapsed time comes from osGetCount, and the port's Count emulation (host-time or instruction-count based)
   returned a short interval for that frame.
 - H-vi: the game derives dt from a VI retrace counter, and the port delivered VIs unevenly (two retraces close together) around
   the flight-onset transition.
 - H-guest: a guest code path (e.g. a load/transition frame handler) legitimately halves dt, reached in the port only because of a
   timing difference upstream.
Discriminator: widen the s7834 dump to the game's timing globals. Both sides, same PC 0x80043918, a window of flight-onset rows only:
dump a wide BSS range (start 0x80110000..0x80140000 in pieces <=1024 words, the oracle cap is PC_RAM_DUMP_MAXW; or raise it) and find
the word that differs at row 2 while every other word matches (scorer: extend tools/s7834_ramdump_cmp.py with a --onset row-by-row mode,
s7834 line 2 did this by hand). Then on retail name its writer with --watch-write on that word (positive control: whole-RDRAM watch)
and read that writer's input (osGetCount vs a VI counter) in the port.
Outcomes: the dt word's source is osGetCount -> H-count (compare the port's Count model, librecomp); a VI counter -> H-vi; equal
inputs but a different guest path -> H-guest. Close the thread with that answer; no further iterations.
Recipes: retail `env CPO=1 RSECS=175 RDPBIN=/dev/null EEP=scratch/s7832/lvl.eep PP=19.5:start,31.5:start,43.5:start,67.5:start,
79.5:start,91.5:start XO="--watch-pc 0x80043918 --pc-ram-dump 0x80043918:<A>:<B>" zsh tools/s7828_retail_cpo.sh OUT`; port
`env SAVE_FROM=scratch/s7832/lvl.eep SECS=150 CAP0=200 AP=6:start,11:start,11.5:w1024,19.5:start,31.5:start,43.5:start,67.5:start,
79.5:start,91.5:start XE="ROGUESQ_AUTOPILOT_CLOCK=vi ROGUESQ_S7834_RAMDUMP=1" zsh tools/g3_port_capture.sh OUT` (the port range is
fixed in tools/apply_s7834_ramdump.py; parametrise it by env first, then regen-gate with s7719 --strict).
