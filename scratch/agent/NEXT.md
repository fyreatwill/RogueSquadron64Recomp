# Next work unit

HYPOTHESIS-ID: m5-first-teardown-deregistration

Implement one bounded behavior change: when the first gate-zero teardown is
about to reapply audio configuration and callback table slot 1 already holds
`0x8009123C`, deregister that existing synth callback once, preserving the
gate value and all later balanced teardown behavior. Keep the existing dedup
control available for rollback.

Competing hypotheses:
- H1: the gate-zero first-teardown skip is the duplicate source; one-shot
  deregistration leaves one synth callback per retrace walk and preserves the
  qualified route controls.
- H2: another registration source or table-order defect remains; the callback
  table still has two live synth entries after the change.
- H3: the change is causally correct but route-invalid or destabilizing; the
  positive callback controls fail before phase qualification.

Discriminator: one build containing the default one-shot change and the
rollback arm, with callback-table slot snapshots, synth entries per retrace,
SP completion, PCM, title/hangar, and crash/abort controls in the same run.
H1 authorizes the bounded default change; H2 pivots to the remaining
registration source; H3 reverts the change and does not generalize the result.

Exact commands:

    rg -n "reapplyAudioConfig|musyxNoopStub|8009123C|800A0F50" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c tools
    python3 tools/apply_s4889_first_dereg.py
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_S4700_CB=1 zsh tools/run_s4889_first_dereg_ab.sh

Do not run the generated-symbol sweep until this M5 unit is closed.
