# Next work unit: M5 Step 5 caller/tail ground truth

HYPOTHESIS-ID: m5-step5-caller-tail-ground-truth

Session 4092 qualified the retail controls and found zero execution at all
eight key-on early-return PCs, despite 50,643 executions of the divisor
publisher `0x80090768`. Do not change or remove the returns.

Competing hypotheses:

- Hdescriptor-branch: `musyxKeyOnVoice` entry `0x80090A3C` executes in the
  target phases, but its `+0x21` descriptor branch never reaches the trap
  sites; the normal tail `0x80090DE8` should provide a positive control.
- Hcaller-gap: the key-on entry itself is absent in target phases, so the
  missing boundary is upstream of `musyxKeyOnVoice`.
- Hcoverage: the oracle whole-RDRAM control or either title/hangar phase is
  absent.
- Hpublisher-misjoin: `0x80090768` is not the relevant target-phase divisor
  publisher despite its observed activity.

Discriminating measurement: one oracle-only run, no build, with the
whole-RDRAM watch first, explicit title/hangar phase gates, and watches on
`0x80090A3C`, `0x80090DE8`, and `0x80090768` together. Entry plus tail with
zero trap activity selects Hdescriptor-branch; zero entry selects Hcaller-gap;
missing control/phase selects Hcoverage; publisher activity without matching
entry/tail phase rows selects Hpublisher-misjoin.

Exact command shape:

`zsh scratch/agent/run_s4093_m5_keyon_entry_tail.sh`

The driver must use the validated Rice video and six-start schedule, kill the
oracle with SIGKILL, and report lifetime plus title/hangar counts for all
three watched PCs. Keep the eight trap watches as controls if breakpoint
capacity permits; do not add runtime instrumentation.
