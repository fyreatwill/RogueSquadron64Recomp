# NEXT work unit (s1157)

HYPOTHESIS-ID: post640-selector-writer-phase

Perform one phase-gated runtime capture tracing the selected post-640 writer
at callsite `0x80019914` through `selectAndApplyViMode` and the following
`osViSetMode` request. Keep the independent selector positive and slot-
dispatch controls. Record ordered committed-width phase, selector bytes,
selected source record, copied-record width, and requested width. Do not add a
mitigation or repeat the closed submitGfxFrame owner capture.

Competing hypotheses and discriminator:

- H1/writer-to-consumer: the post-640 selector change is followed by a changed
  selected record or requested width.
- H2/transient-selector: the selector changes but the consumer remains on the
  old record/width, so the write is unrelated to descriptor selection.
- H3/ordering-gap: the writer change is observed but no selector consumer runs
  afterward in the same phase.

The discriminating measurement is one ordered phase-scoped writer/consumer
table with an independent positive control: changed selector followed by a
changed consumer selects H1; unchanged consumer selects H2; no consumer row
after the writer selects H3. Missing controls or missing post-640 rows is
inconclusive.

Commands (from the repository root):

    python3 tools/apply_s802_vi_selector_probe.py
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    env PROBE_PHASE_WIDTH=640 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 ROGUESQ_LOG_VI_WRITERS=1 ROGUESQ_LOG_VI_SELECTOR=1 ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_VI_TRANSITION=1 zsh tools/probe.sh scratch/agent/s1157_vi_consumer 180 0.5
