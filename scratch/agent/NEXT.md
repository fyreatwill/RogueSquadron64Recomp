# NEXT (s7790; s7789 closed the quiet-skip class: 165 dead vendored .replace sites, all reviewed, census = s7719 step 5c)
HYPOTHESIS-ID: vendored-dead-block-prune
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Unit (offline, engineering): delete the confirmed-dead inline blocks from tools/fixup_game_funcs_vendored.py (42.5k lines).
List: `python3 tools/s7789_replace_site_census.py --keep /tmp/s7790 --all --json /tmp/s7790/rows.json`; candidates = rows with
st NOTCALLED/MISS and pres ABSENT whose REVIEWED verdict says RETIRED (s109 + s390-s568 item -317 lineage) or diagnostics.
Delete whole blocks (from the block's leading comment to its report.append), never a lone .replace line. Keep: OPTIN modes,
PRESENT rows (another route may depend on the block order), s147 (document only).
Hypotheses: H-inert (the replay tree stays byte-identical: s7719 --strict VERDICT H-mirrored), H-coupled (a later block keys on a
deleted block's marker/variable: the replay diverges or the fixer raises NameError -> restore that block, record the coupling).
Proof: `python3 tools/s7719_regen_gate.py --strict` rc 0 + live == replay, census re-run (HIT count unchanged 326, open=0),
`python3 tools/s7651_gate_sweep.py --only 's77'`. Report net lines removed.
