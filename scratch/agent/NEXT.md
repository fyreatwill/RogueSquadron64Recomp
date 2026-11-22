# NEXT (s7787; s7786 closed the load-hook class: 0 mixups, 4,447 unwatched loads + 2 mislabelled s4307 pcs fixed)
HYPOTHESIS-ID: hook-pc-literal-census
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines. **Fold soak s7786_uafload_full** (class EI re-run with full load coverage):
rc 0 + plant DETECTED every arm -> EI closed at full coverage (update CURRENT-TRUTH item 33); any load_F/Urec row reopens EI and
names the reader pc (check whether that pc is one of the 4,447 newly watched loads: then s7484's old null was a coverage hole).

Question: does every pc LITERAL passed to a diagnostic hook equal the pc of the instruction it sits under? s7786 found the s4765
spin2 rewrite dropping a pc comment, so the s4307 join tagged two loads with the previous instruction's pc. Generalise:
Families: every `rs64_*(..., 0x8XXXXXXXu, ...)` / `RS64_*(0x8XXXXXXXu, ...)` call and every `g_rs64_last_guest_pc = 0x...u;`
in the generated tree, keyed per function to the nearest preceding `// 0x<pc>:` comment.
Hypotheses: H-clean (every literal == its comment pc, or a documented site constant), H-shift (some fixup emits a neighbouring pc,
like s4307 at DC4/F34), H-pcless (other rewrites emit pc-less comments: count `// <op>` comments without 0x; s7786 found 2, both spin2).
Unit (offline): tools/s7787_hook_pc_census.py (--controls: planted literal off by 4 must read bad, a pc-less comment must be listed);
classify every mismatch (site-constant hook that names a function entry/branch target on purpose = KNOWN row, else fix the emitter
in its apply_*/fixup script, idempotent), rebuild, s7719 --strict, sweep. Outcomes: 0 unexplained -> H-clean, close; else name the
emitter and list conclusions that read that hook's pc (grep PORTING-STATE for its env var).
