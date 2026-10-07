# Next work unit: M5 Step 5 retail key-on/divisor ground truth

HYPOTHESIS-ID: m5-step5-keyon-ground-truth

Session 4091 qualified the first downstream return boundary: the port
`stage=return v0` values matched the low-16-bit `s0` support observed at the
retail `0x80084AB8` instruction boundary. The next M5 unit is the required
ground-truth prerequisite for the eight key-on early-return sites; it does
not remove or relax any return yet.

Competing hypotheses:

- Hvalid-divisor: retail reaches the key-on sites with an in-range divisor
  published by `0x80090768`, so a later port A/B can audit the early returns.
- Hreturns-dead: no target-phase key-on site is reached, so the returns are
  not the current M5 boundary.
- Hcoverage: the oracle positive control or either target phase is absent.
- Hwriter-mapping: the watched divisor publisher is not the actual value
  writer or its phase attribution is inconsistent.

Discriminating measurement: one oracle-only ground-truth capture must fire the
whole-RDRAM positive control and both target phase gates, then report all eight
key-on PCs (`0x80090CEC`, `0x80090D04`, `0x80090D30`, `0x80090D48`,
`0x80090D74`, `0x80090D8C`, `0x80090DB8`, `0x80090DD0`) plus the known divisor
publisher `0x80090768`. In-range divisor evidence and target-phase site hits
select Hvalid-divisor; zero target-phase site hits select Hreturns-dead; a
missing control/phase selects Hcoverage; inconsistent publisher/value rows
select Hwriter-mapping.

Exact preparation:

1. Do not build or add runtime instrumentation before the oracle measurement.
2. Create a self-contained oracle driver from the repo root, with `--watch-pc`
   containing the whole-RDRAM watch, all eight sites, and `0x80090768`.
3. Use the existing title/hangar phase gates and synthetic keypress schedule;
   terminate with SIGKILL and summarize counts by phase.
