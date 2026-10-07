# Next work unit: M5 Step 5 port boundary qualification

HYPOTHESIS-ID: m5-step5-port-boundary-qualification

Session 4093 qualified retail caller/tail ground truth: entry `0x80090A3C`
and normal tail `0x80090DE8` both execute in title/hangar, while all eight
early-return PCs remain zero; `0x80090768` is active in both phases. Do not
change or remove the returns.

Competing hypotheses:

- Hport-descriptor-branch: port entry and tail execute with zero early-return
  witnesses, matching retail; the gap is in the descriptor branch.
- Hport-caller-gap: port entry is absent while the route controls qualify.
- Hport-returns-live: port early-return witnesses fire, contradicting the
  retail boundary or exposing a recomp divergence.
- Hcoverage: the port route or phase controls fail, so port nulls are invalid.

Discriminating measurement: one same-build declared-real port run with the
existing route/PCM controls and one batched phase-gated diagnostic covering
entry `0x80090A3C`, tail `0x80090DE8`, all eight early-return PCs, and
publisher `0x80090768`. Entry/tail plus zero traps selects
Hport-descriptor-branch; zero entry with route controls selects
Hport-caller-gap; any trap hits select Hport-returns-live; absent route/phase
controls selects Hcoverage.

Exact command shape:

`zsh scratch/agent/run_s4094_m5_port_keyon_boundary.sh`

The driver must run from `build/`, use the validated declared-real route,
phase-gate title and hangar, and report route controls plus lifetime and phase
counts for all eleven watched PCs. Keep all arms in one build/run; do not
alter generated returns or add an oracle-only replacement.
