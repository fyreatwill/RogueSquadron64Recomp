# Next work unit: M5 Step 6 descriptor-branch comparison

HYPOTHESIS-ID: m5-step6-descriptor-branch-comparison

Session 4094 qualified the declared-real port boundary: the clean run reached
title and hangar, port entry/tail both counted 102806 in the hangar bucket, and
all eight early-return guards stayed zero. Do not change or remove the returns.

Competing hypotheses:

- Htuple-match: retail and port descriptor-branch tuples match, moving the
  unresolved boundary downstream.
- Htuple-diverge: the first tuple mismatch identifies the port divergence.
- Hpublisher-gap: the publisher/branch join is absent despite valid phases.
- Hcoverage: either positive control or target phase is absent.

Discriminating measurement: extend the existing one-run retail oracle and
declared-real port capture to batch the descriptor branch's phase-gated
register/pointer tuple alongside entry `0x80090A3C`, tail `0x80090DE8`, all
eight returns, and publisher `0x80090768`. Matched tuples select Htuple-match;
the first mismatch selects Htuple-diverge; missing publisher join selects
Hpublisher-gap; absent controls select Hcoverage.

Exact starting command:

`zsh scratch/agent/run_s4094_m5_port_keyon_boundary.sh`

Extend the driver before execution with the retail tuple watch, run from
`build/` on the validated declared-real route, phase-gate title and hangar,
and report the complete tuple table. Keep all arms in one build/run; do not
alter generated returns or add an oracle-only replacement.
