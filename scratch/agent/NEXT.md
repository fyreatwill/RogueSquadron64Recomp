# Next work unit

HYPOTHESIS-ID: m5-retire-synth-dedup

Change the default of the existing `s4878` synth-registration deduplication
arm to off. Keep `ROGUESQ_S4875_DEDUP=1` as the rollback arm and keep the
s4890 one-shot first-teardown deregistration enabled. This tests whether the
named origin fix makes the mitigation redundant.

Competing hypotheses:

- H1: after s4890, dedup can be retired; default-off has one synth callback per
  retrace and preserves SP/PCM/title/hangar controls.
- H2: another duplicate source remains; default-off shows two synth callbacks
  or a route divergence while rollback remains qualified.
- H3: dedup is not the duplicate source but is a stability guard; default-off
  crashes or loses the qualified route despite one callback entry.

Discriminator: one build containing default dedup-off and rollback dedup-on,
run concurrently with `ROGUESQ_S4889_FIRST_DEREG=1`, callback-table snapshots,
synth entries/deregistrations, `[m5-route-order]` SP completion, PCM boundary,
title/hangar, and crash/abort controls. H1 authorizes removing the default
mitigation; H2 keeps it and audits the remaining registration source; H3 keeps
it and treats the one-shot fix as insufficient for retirement.

Exact commands:

    python3 tools/apply_s4891_retire_synth_dedup.py
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh tools/run_s4891_retire_synth_dedup_ab.sh

Do not start the generated-symbol sweep while this M5 unit is applicable.
