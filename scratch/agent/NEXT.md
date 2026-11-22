# NEXT (s7791; s7790 pruned 257 dead vendored blocks, -5,090 lines, replay byte-identical)
HYPOTHESIS-ID: vendored-dead-block-prune
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines. CURRENT-TRUTH is ~60 KB: if Step 0 trips, do maintenance instead.

Unit (offline, engineering, last step of this campaign): the NOTCALLED:PRESENT rows (392 sites after s7790) are blocks that
never ran in the pristine replay while their text exists in the live tree via another route (shadowed duplicates). Extend
tools/s7790_prune_dead_blocks.py with `--shadowed`: a loop-level block qualifies when ALL its sites are NOTCALLED (none ran),
>=1 is PRESENT, none OPTIN, no os.environ, and the census shows the distinctive text PRESENT in the replay's own output
(so an earlier step emits it). Dry-run first and spot-read 10 blocks: if any is a guard whose `if marker in text: continue`
idempotence check is the ONLY reason it skips (it re-applies after an earlier step is removed), keep that family.
Also split the 12 H-coupled blocks: keep the table binder, drop the dead loop.
Hypotheses: H-inert (s7719 --strict H-mirrored, live == replay), H-order (a shadowed block is the fallback for an earlier
route that could stop emitting: deleting it is still inert today; record which ones are fallbacks in the ledger).
Proof: `python3 tools/s7719_regen_gate.py --strict` rc 0, census HIT 326, `python3 tools/s7651_gate_sweep.py --only s77`.
Then close the campaign and take the next ladder rung (CURRENT-TRUTH Next steps / item 3c).
