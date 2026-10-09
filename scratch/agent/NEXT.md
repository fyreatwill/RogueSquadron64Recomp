# Next work unit (s4469): M5-AUDIO-PLAN step 5 - audit the eight key-on early returns as one idiom class

HYPOTHESIS-ID: m5-keyon-early-return-audit

Context: the s4465 heap-overlap lead is parked (unreproduced 0/8). Strategic priority 2 (M5) and rule 14 call for an engineering change, not another diagnostic field.
Hypotheses: (A) the eight key-on early returns in the generated/fixup code are dead or only hit on invalid descriptors (safe to keep as guards, document); (B) some fire on valid hangar descriptors and drop real voices (candidate de-stub); (C) they are unreachable in current runs (needs a positive control).
Step: read docs/M5-AUDIO-PLAN.md step 5 and its inventory row; grep-enumerate every key-on early-return site in tools/fixup_*.py; classify each (writer of the guarded value, legit range); add per-site hit counters in ONE build, with a "mark everything" control; one hangar run (phase-gated at VI 512). Outcome A -> close class with proof; B -> relax the firing sites in the fixup scripts with an ORIGIN: line; C -> note and queue a soak.
