# Next work unit: witness the qualified predecessor on the port

HYPOTHESIS-ID: m5-step4-object-field-producer

Use the qualified s4177 retail boundary. Add a regeneration-safe port witness at
`0x8008F900`, whose retail predecessor is `0x8008F8FC`, and join it to the
existing port-side witness at `0x80090268`, `0x80090278`, and
`0x8008FF04/0C/14` in the title/hangar phases. Keep the qualified
real-audio/LLE/ungated/solo route and all positive controls.

Before building, compare the new witness against these hypotheses:

- H-entry-context-match: the port entry snapshot joins retail-like object
  fields, moving the mismatch downstream.
- H-earlier-producer-mismatch: the entry context is already divergent, keeping
  the source boundary at or before `0x8008F900`.
- H-route-invalid: the whole-RDRAM control or either title/hangar phase is
  absent, so the retail result is unevaluable.

The discriminator is the same-run retail/port entry-context join: matching
context moves the boundary downstream, an already-divergent context keeps it
at or before `0x8008F900`, and missing controls/phases rejects the run. No
audio, gate, writer, payload, or mitigation behavior change is authorized.

Build with the normal CMake target, then run a phase-gated paired recipe
derived from `scratch/agent/run_s4175_m5_object_entry.sh`, adding the port
witness at `0x8008F900`. Keep all existing positive controls and passive
breadcrumbs.
