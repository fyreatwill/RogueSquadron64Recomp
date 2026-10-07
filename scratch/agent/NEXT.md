# Next work unit: locate the executed entry before the divergent object fields

HYPOTHESIS-ID: m5-step4-object-field-producer

Use the qualified s4175 route as the base. The port-side witness at
`0x80090268`, `0x80090278`, and `0x8008FF04/0C/14` fired in title/hangar, but
its `s0+0x60`, `s0+0x22`, and `s1+0x22` values did not reconcile with the
independent retail oracle. Do exactly one independent retail predecessor
measurement before adding another port witness. Use the oracle's
`--watch-pc-range` over the static `0x8008F9C8` candidate and its surrounding
function range, plus the existing exact target-PC watches, whole-RDRAM control,
`--pc-field-dump`, and title/hangar phase gates. Keep the qualified
real-audio/LLE/ungated/solo port route in the recipe for route comparison.

Before building, compare the new witness against these hypotheses:

- H-static-entry-unexecuted: the range confirms `0x8008F9C8` is not entered;
  select the first executed predecessor/entry PC from the range histogram.
- H-earlier-producer-mismatch: an executed earlier PC supplies the object or
  field inputs; that PC becomes the next port witness boundary.
- H-route-invalid: the independent positive control or title/hangar phase is
  absent; the range result is unevaluable.

The discriminator is the same-run range/predecessor table: a nonzero exact
entry/range hit identifies the next boundary, zero exact entry hits with live
target PCs rejects the static candidate, and a missing control/phase rejects
the run. No audio, gate, writer, payload, or mitigation behavior change is
authorized.
