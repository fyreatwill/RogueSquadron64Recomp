# NEXT work unit (s1172)

HYPOTHESIS-ID: musyx-downstream-ground-truth-pointer-origin

Run one ground-truth-assisted pointer-origin experiment for the first
unresolved MusyX sample/stream pointer path identified at
`musyxRenderVoiceSamples` (`0x8009004C`–`0x80090050`). Consult
`tools/oracle/README.md`, arm a whole-RDRAM positive control, and add one
physical watch covering the retail voice-array/sample-pointer region that
corresponds to the port-side `0x801496F8` voice base. Build all watch/control
arms together and phase-gate the result. Do not add a mitigation.

Competing hypotheses and discriminator:

- H1: retail writes the watched voice/sample-pointer field before the
  corresponding port-side operation, identifying a legitimate game writer.
- H2: retail reaches the phase and positive control but never writes the
  watched field, moving origin to command-list/submission or an unmodeled
  runtime path.
- H3: the oracle remains pre-audio or the target range is not reached, so the
  pointer-origin question is unevaluable.

The s1171 census result was H3 for the port-only operation table: the first
possible wild pointer is a voice/sample field load, but its runtime writer and
legitimacy are unresolved. The next measurement must therefore be independent
retail write attribution, not another port-side field.

Exact commands:

    sed -n '1,140p' tools/oracle/README.md
    rg -n "whole-RDRAM|watch-write|positive control|physical" tools/oracle/README.md
    rg -n "voice|musyx|audio|phase|watch" scratch/agent tools/oracle docs | head -120
    git status --short

Record whole-RDRAM callback count, watched-range writes, PC attribution, and
phase reachability. If the watch is not physically mappable or the positive
control fails, record H3 and choose a corrected oracle arm; do not infer a
null origin result.
