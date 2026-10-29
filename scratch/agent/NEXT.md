# NEXT: reconcile objective-response coverage from saved evidence
HYPOTHESIS-ID: g1-coverage-cd

One bounded offline tool/report change: build a reproducible per-level G1(d)
evidence table from saved ctl/TELE logs, then choose the first missing
level-specific response. Do not run the game in this unit.

Hypotheses:
- H-response: a phase-scoped, named objective counter changes under forced
  hits and its meaning matches that level's objective, with a firing hit
  positive control; existing evidence suffices for that counter response.
- H-incidental: only damage/writer-call counts or fail counters change, or
  the same transition occurs in ctl; objective success response is unproven.
- H-missing: logs, phase keys, counter meaning or a firing hit control are
  absent; keep the level unknown rather than treating zero as a result.

Discriminator: one table with level, route identity, log/phase provenance,
TELE firing, exact counter id and transition, matched ctl transition,
success/failure semantics and evidence source. An end callback occurring
in both arms is not a hit-driven end gate. No new mission wins/progression,
aim, bolt tracking or repeat crash holds. Two independent lines before
promoting an established fact; otherwise label single-source.

Commands from repo root (bounded ledger windows only):
    rg -n '^## Session (594[6-9]|595[0-9]|596[0-2]|599[3-6])' PORTING-STATE.md
    sed -n '1,160p' tools/g1_d_compare.sh
    sed -n '1,180p' tools/objsnap_summary.py
    rg --files scratch/agent/soak_results | rg 'g1_lvl.*(ctl|tele)'
    rg --files scratch/agent/m6 | rg 'g1_lvl.*(ctl|tele)/run.log$'

Inspect <=60-line windows at the relevant ledger hits. Stream plain/gzip
logs to extract only phase, sph TELE, objsnap/objsnap-t and objcount lines;
never dump a full log. Read existing parsers before reusing them: raw writer
call counts and run-lifetime maxima are insufficient. Add a bounded report
or extend an existing parser to print the whole table, checking a known
nonzero lvl7/lvl8 transition as the positive control and the corresponding
ctl and ambiguous lvl9 as controls. Do not manufacture phase keys if old
logs lack them. Name the first level-specific missing discriminator and
its exact saved recipe for the following unit. Missing files are evidence
limits, not human blocks. This is not an excuse to re-open aim or wins.
