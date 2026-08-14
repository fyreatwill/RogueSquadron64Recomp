# NEXT work unit (s1158)

HYPOTHESIS-ID: post640-selector-writer-phase

Perform one phase-gated runtime capture that explains the s1157
non-reproduction before attempting consumer ordering. Instrument the
`applyPendingViChanges` callsite `0x80019914` with its pending selector inputs,
all three selector bytes, and the exact store path; retain the independent
selector-positive and slot-dispatch controls. The capture must distinguish:

- H1: the pending input is unchanged from s1156 and the selector store path is
  wrong or not reached, so the probe's observed bytes are not the causal state;
- H2: the pending input itself is zero/unchanged in this run, so the s1156
  selector transition is phase/input-dependent;
- H3: the input is nonzero and the store executes, but the expected selector
  bytes remain unchanged, identifying an address/endian/measurement defect.

The discriminating measurement is an ordered table at `0x80019914` containing
pending inputs, pre/post selector bytes, and store-path evidence after
committed width 640. The selector-positive and slot-dispatch controls must
fire; missing controls or missing post-640 callsite rows is inconclusive.

Commands:

    python3 tools/apply_s802_vi_selector_probe.py
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    env PROBE_PHASE_WIDTH=640 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 ROGUESQ_LOG_VI_WRITERS=1 ROGUESQ_LOG_VI_SELECTOR=1 ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_VI_TRANSITION=1 zsh tools/probe.sh scratch/agent/s1158_selector_writer_inputs 180 0.5

Expected outcomes: H1 selects a measurement/address defect; H2 selects an
input/state-path difference and sends the next probe to its writer; H3 selects
the store/address implementation defect. Otherwise leave the thread open as
unevaluable and do not infer a consumer result.
