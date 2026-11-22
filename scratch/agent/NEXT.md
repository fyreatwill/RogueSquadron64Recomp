# NEXT (s7825)
HYPOTHESIS-ID: g3-logo-quarter-pixel
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7824 --tri-geom: STAR WARS logo zoom tris differ from retail by exactly one s13.2 LSB on ~10% of tris (176/266 frames);
crawl exact. Our RSP == patched cxd4 (s7815), so the RSP input differs. Decide which CPU is wrong.
Hypotheses: H-cpu (recompiled float/fixed math, e.g. a cvt/trunc/round or float->s16 path, differs from MIPS) / H-oracle-cpu
(mupen64plus core FPU emulation is the inaccurate one) / H-input-time (the logo state is fed a wall/VI-derived value that differs).
Discriminator, one run each side, offline compare:
 1. Oracle `--det` RDRAM dump at a logo VI where s7824 retail frame mismatches (retail frames 2720:2986; dumps via the
    s7816/s7817 oracle scripts), and the port's RDRAM at the same game state (ROGUESQ dump flag used by g3 tools).
 2. Feed the RETAIL dump's gfx task through tools/s7752_port_task/harness (our LLE): output == retail rdplog tris -> input differs
    (H-cpu or H-oracle-cpu); then diff the logo vertex/matrix buffers between the two dumps to name the field and the writer.
 3. Writer named -> reproduce its float ops in a tiny C test on both a MIPS reference (mips64-elf-gcc + an interpreter, or CEN64)
    and host: which result matches real MIPS semantics decides H-cpu vs H-oracle-cpu.
Data: scratch/s7824/{retail,port}.bin.zst; `python3 tools/s7821_rdp_screen_segments.py R P --windows 2686:2985,3485:3790,3349:3484 --tri-geom`.
If the dumps cannot be aligned within 2 iterations, close as single-source (1/4 px, invisible) and resume g3-det-menu-pair at the
first mission frames (one more START after the crawl).
