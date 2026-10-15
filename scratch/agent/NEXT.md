# Next work unit

HYPOTHESIS-ID: external-retail-entry-new-pc-discriminator

Run one independent retail-oracle capture that keeps the qualified
whole-RDRAM, title, and hangar controls but watches the complete
`musyxRenderVoiceSamples` execution range `0x8008FFAC:0x80090640`, plus the
two statically identified voice `+0x34` writers `0x80090C80` and `0x800921E8`.
Use phase-gated rows for title `0x00790400:1024` and hangar
`0x006AB400:512`; do not repeat the old `0x800903F0`-only watch.

Before building any instrument, read `tools/oracle/README.md` and reuse the
existing qualified Rice/input launch recipe. Capture the exact command and
output under `scratch/agent/soak_results/` (or a self-contained queued script
if the run exceeds the iteration window). Positive control: whole-RDRAM watch
must reach 10,000, and both title and hangar VI controls must fire.

Competing hypotheses and discriminator:

* H1: the retail route reaches the voice-render function but not the selected
  consumer instruction; range hits plus phase writer activity prove an
  internal consumer/branch boundary.
* H2: the route reaches the voice-render range and selected consumer, but the
  prior single-PC watch missed due to breakpoint/PC attribution; range hits and
  a `0x800903F0` hit select a watch artifact.
* H3: the qualified retail route has no phase-gated voice-render range hits;
  the external handoff is genuinely route-absent and this thread closes.

The result must include the positive controls and phase-gated counts for all
three arms (range, writers, exact consumer). Do not infer a writer or land a
mitigation from a null. If the launch is unavailable, record the concrete
failure and do not substitute another diagnostic.
