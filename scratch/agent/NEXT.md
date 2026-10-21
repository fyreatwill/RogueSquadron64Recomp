# NEXT: read the [lvsel] lines from s5704_lvsel_f3 / s5704_lvsel_f0 (scratch/agent/m6/<TAG>/run.log; grep '\[lvsel\]')
Hypotheses: H1 unlock mask (a2) < needed; H2 cursor init ignores B40 (a1 mask); H3 injected keys move cursor; H4 stale pad state.
Discriminator: init a1/a2 vs forced B40 on f3 arm, plus tick-by-tick cursor/ret. f0 arm is the control (tick#1 line must appear in both).
Then: force result N at the 0x800C5ED8 store under an env knob (fixup script) and run lvN.
HYPOTHESIS-ID: g1-level-select
