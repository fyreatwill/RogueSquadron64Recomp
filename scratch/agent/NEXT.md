# Next work unit: witness the executed entry before the divergent object fields

HYPOTHESIS-ID: m5-step4-object-field-producer

Use the qualified s4176 route as the base. Add a regeneration-safe port witness
at `0x8008F900`, whose retail predecessor is `0x8008F8FC`, then join it to the
existing port-side witness at
`0x80090268`, `0x80090278`, and `0x8008FF04/0C/14` fired in title/hangar, but
its `s0+0x60`, `s0+0x22`, and `s1+0x22` values did not reconcile with the
independent retail oracle. Do exactly one independent retail predecessor
measurement before adding another port witness. Use the oracle's
`--watch-pc-range` over the static `0x8008F9C8` candidate and its surrounding
function range, plus the existing exact target-PC watches, whole-RDRAM control,
`--pc-field-dump`, and title/hangar phase gates. Keep the qualified
real-audio/LLE/ungated/solo port route in the recipe for route comparison.

Before building, compare the new witness against these hypotheses:

- H-entry-context-match: the new port entry snapshot joins retail-like object
  fields, moving the mismatch downstream.
- H-earlier-producer-mismatch: the entry context is already divergent, keeping
  the source boundary at or before `0x8008F900`.
- H-route-invalid: the build or phase-gated run lacks its positive control or
  title/hangar phases, so the witness is unevaluable.

The discriminator is the same-run retail/port entry-context join: matching
context moves the boundary downstream, an already-divergent context keeps it
at or before `0x8008F900`, and missing controls/phases rejects the run. No
audio, gate, writer, payload, or mitigation behavior change is authorized.

Build with the normal CMake target, then run the phase-gated paired recipe
derived from `scratch/agent/run_s4175_m5_object_entry.sh`, replacing its static
entry witness with `0x8008F900`. Keep all existing positive controls and
passive breadcrumbs.
