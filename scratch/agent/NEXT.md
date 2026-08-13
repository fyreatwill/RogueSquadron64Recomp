# NEXT work unit (bounded E9/FULL_SYNC accounting-boundary audit)

HYPOTHESIS-ID: m3-postsec2-authoritative-e9

Perform one read-only source/telemetry audit. Trace every write, reset, cap, and
log site for aligned-E9 counts (`e9_a/e9_b/e9_aligned`) and authoritative
`rdpFs`/`[rdp-fullsync]` counts, including task/phase scoping. Do not build, run,
change game logic, or add a mitigation.

Competing hypotheses:

- H-same-population: both counters are intended to measure the same command
  population, so their divergent rates imply a real parser-chain loss or
  sampling defect.
- H-different-populations: the counters are scoped to different task/stream
  populations or parser stages, so the divergence is expected and cannot by
  itself establish command loss.
- H-counter-defect: one counter is reset, capped, or joined at the wrong task
  boundary, so the observed divergence is instrumentation accounting error.

Discriminating measurement: a complete source map of producer/reset/cap/task
scope for both counters. If scopes match, H-same-population remains live; if
they differ, H-different-populations is selected; if a reset/cap/join defect is
found, H-counter-defect is selected. The s820 and s821 captures are the
independent runtime line of evidence; the audit must not treat runtime output
as its own ground truth.

Exact commands:

    rg -n "e9_a|e9_b|e9_aligned|rdpFs|rdp-fullsync|RDP.*advance|fullSync" src lib ../N64Recomp/RecompiledFuncs
    rg -n "e9_a|e9_b|e9_aligned|rdpFs|rdp-fullsync" docs scratch/agent/PORTING-STATE.md 2>/dev/null

Record the exact producer/reset/cap sites and update the ledger with the
selected accounting hypothesis. If the audit cannot distinguish them, leave
the parser discrepancy open and choose the smallest next source probe.
