# Maintenance: compact CURRENT-TRUTH before another experiment
HYPOTHESIS-ID: current-truth-maintenance

s6666 ended with CURRENT-TRUTH61170 bytes,708 lines. Step0 therefore
triggers mandatory maintenance next iteration. Do NOT build or run a game.
The s6666 flight selected H-duration: old5401VI reaches timer55.5496902;
natural threshold100.033333 at9839VI sets21/59, rescue01 appears, exact
force/SEND/ordinary damage2000->1990. Counter40 remains0 legitimately.
The complete result and remaining loss-response work are in
G1-OBJECTIVE-RESPONSE.md s6666 and CURRENT-TRUTH live Next steps.

ONE bounded change: compact CURRENT-TRUTH toward35KB with>=200 net lines
removed. Migrate durable per-level(c) capture paragraphs and duplicate G1
coverage details to PROJECT-OVERVIEW (existing coverage report also retains
them); move historical colliding archived backlog sequences and Update
s6568 history there. Preserve current configs, constraints, open boundaries,
s6666 evidence limits and the ONE current monotonic backlog. Refresh headline
and evidence index to the new session. Do not change runtime or enqueue soaks.

Competing structural explanations / discriminator:
- H-history: obsolete next-step chains and repeated per-level evidence are
  most of the excess. Move them with source/session labels; links must lead
  to retained durable material and active handoff must still be complete.
- H-active: material is still needed to choose/run the next experiment. Keep
  actionable constraints and exact commands in the compact file; do not
  discard them just to meet a line target.
Measurement: byte count, git numstat net-line shrink>=200, retained evidence
links and one monotonically numbered live backlog. If shrinking is achieved
by deleting current blockers/constraints, maintenance fails regardless of size.

Commands, in order:
    cat docs/CURRENT-TRUTH.md
    cat scratch/agent/NEXT.md
    tail -20 scratch/agent/SOAK-RESULTS.md
    wc -c < docs/CURRENT-TRUTH.md
    wc -l docs/CURRENT-TRUTH.md docs/PROJECT-OVERVIEW.md
    rg -n '^## |^### |^-?[0-9]+\.' docs/CURRENT-TRUTH.md
Read overview only in bounded windows around insertion points; never whole.
Use a scripted move of exact blocks, then verify their text in overview.
    git diff --numstat -- docs/CURRENT-TRUTH.md
    git diff --check
    rg -n '^## Session ' PORTING-STATE.md | tail -2
Append Session6667 ledger, update CURRENT-TRUTH and rewrite NEXT for the
first live backlog item with its whole competing-hypothesis table. Commit
with iter: message, STATUS DONE, OUTCOME ADVANCED only if net shrink>=200.
No experiment is part of this maintenance unit.
