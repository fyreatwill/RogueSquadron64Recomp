# Next: new-angle M4 accumulator boundary revisit.

The s5250 baseline arm self-skipped at host load1=5.20, so do not retry it
until a future loop supplies load1<2. M5 has no uncompleted de-stub step and
the recent M3 idiom classes are closed. Session 5278 ruled out a distinct
caller population at the retail-entry boundary but left dynamic `a1`
unresolved. The recent 15-session census is sweep-scoped, so do not resume
symbol classification yet.

Competing hypotheses and discriminator:

- H1: the M4 accumulator difference is a mid-task RSP state/value contract
  that task-end counts cannot see.
- H2: the difference is introduced by task publication or DMA ordering before
  the RSP accumulator is sampled.
- H3: the remaining accumulator difference is measurement-only; a same-task
  mid-task join will match retail and port.

Discriminating measurement: use one phase-gated retail oracle run with the
existing `--pc-task-dump 0x80033FCC --pc-task-type 2` and the M4 accumulator
watch/decoder from `scratch/agent/s5129_m4_mid_acc`, adding one positive
whole-RDRAM watch and one task-end control in the same run. H1 predicts a
mid-task accumulator row mismatch with matched task publication; H2 predicts
publication/DMA ordinal mismatch before the accumulator row; H3 predicts
matching mid-task rows and ordinals. A whole-RDRAM positive control and both
hangar VI controls must fire before a null matters.

Exact preparation command: `rg -n "8000|pc-task-dump|mid-task|accumulator|ordinal" scratch/agent/s5129_m4_mid_acc docs/REVISIT-S5129-AUDIT.md tools/oracle`

HYPOTHESIS-ID: m4-accumulator-boundary-revisit
