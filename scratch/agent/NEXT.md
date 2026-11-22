# NEXT (s7785; s7784 closed item 32: the s5660 unaligned-store hook reported the VALUE register as the address, all 404 sites)
HYPOTHESIS-ID: s5660-hook-fallout
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Datum (s7784): before s7784, rs64_s5660_ustore got `value + offset` instead of `base + offset` for every swl/swr/sdl/sdr store, and
it forwards to rs64_s6843_note (STORE_WATCH [swatch]/[swatch-pt], s7779/s7781/s7783 FB-arena) and the s5654 vstore census. Fixed
in tools/apply_s5660_unaligned_store_census.py; gate tools/s7784_ustore_base_census.py.

Question: which recorded conclusions relied on unaligned-store addresses from that hook, and does any flip?
Hypotheses:
- H-none: every other conclusion rested on aligned stores (rs64_s6843_store, correct) or host writes; the swl/swr share was 0 or noise.
- H-false-hit: some [swatch] hit attributed to an unaligned pc was a value that happened to fall in the watch range (a false writer).
- H-missed: a real unaligned writer of a watched range was missed (its value fell outside) -> some "writer not found" null is void.

Unit (offline, no game run unless a flip needs re-measurement):
1. Pc set: `grep -ho "rs64_s5660_ustore(0x[0-9A-F]*u" ../N64Recomp/RecompiledFuncs/funcs_*.c | sort -u` (404 pcs).
2. Scan retained logs (scratch/**/run.log, scratch/agent/soak_results/*.log) for [swatch] / [s6843] / [s7779] / [s7781] / [vstore] hit
   rows whose pc is in the set; tabulate per session dir. Write tools/s7785_ustore_fallout.py (control: s7783b must show the DL
   swl pcs as hits; s7784b must show them with in_slot 0).
3. For each session with hits, grep its PORTING-STATE entry: did the conclusion name an unaligned pc as a writer, or rest on a null
   that unaligned stores could have filled (H-missed)? Classify each: unaffected / flipped / needs re-run.
4. Any "needs re-run" that is a live owner-facing question -> queue a soak with the fixed binary; else record and close.
Outcomes: all unaffected = H-none, close the fallout; any flipped = supersede that conclusion in CURRENT-TRUTH with why.
