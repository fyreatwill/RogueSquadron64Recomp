# NEXT work unit (s1156)

HYPOTHESIS-ID: post640-selector-writer-phase

Perform one phase-gated runtime capture tagging every callsite of the two
generated selector-writer families found in s1155: the two
`buildAndRegisterDefaultMaterial` callers (`0x800183F8` and `0x800185DC`) and
the `applyPendingViChanges` entry (`0x8001B7F0`). At each writer, record the
committed VI phase, old/new values of selector bytes
`0x8011A862/0x8011A864/0x8011A865`, and the writer callsite. Keep the
independent selector positive control and slot-dispatch control. Do not add a
mitigation or repeat the closed submitGfxFrame owner capture.

Competing hypotheses and discriminator:

- H1/causal-selector-writer: a tagged generated writer changes a selector byte
  after the final committed 640 record.
- H2/post640-no-change: a tagged generated writer runs after 640 but leaves the
  selector values unchanged, so it is not the cause of descriptor selection.
- H3/no-post640-writer: no tagged generated writer runs after 640; the remaining
  owner is non-generated or an untagged path.

The discriminating measurement is one phase-scoped writer table with old/new
selector values and an independent positive control: a post-640 value change
selects H1; a post-640 entry with unchanged values selects H2; no post-640
entry with controls live selects H3. Missing controls or missing phase rows is
inconclusive.

Commands (from the repository root):

    python tools/apply_s802_vi_selector_probe.py
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_VI_WRITERS=1 ROGUESQ_LOG_VI_SELECTOR=1 ROGUESQ_LOG_SLOT_DISPATCH=1 zsh scratch/agent/run_vi_phase_gate.sh

If the existing probe script is not the right hook for the writer callsites,
make one batch instrumentation edit and run both writer arms in that one build;
do not spend a build-run cycle per counter. Record the phase-positive controls,
the complete writer table, and the selected outcome in the ledger and
CURRENT-TRUTH.
