# Session 3236 — M5 Step 3 contract-edge selection

The Step 3 selection was performed against the M5 inventory, the Step 1
contract-pair evidence, and the Session 3235 same-build qualification.

Competing hypotheses:

- `H-AudioDegeneracy`: the silent path causes downstream audio failure.
- `H-ImageContract`: one proven image task/output edge is missing.
- `H-PortRoute`: the pre-title route stop precedes the audio contract.

Discriminator: a candidate edge must have independent retail and port
evidence for writer PC, destination span, payload polarity, and completion
ordering, and must be observable at the requested title/hangar phase.

Result: no candidate qualified. Session 3235's positive-controlled retail
run reached title and hangar, but both same-build port arms stopped at VI 640
before the target phase. Their dispatch controls passed; all task/output,
service, slot, voice, MORT, and PCM joins were therefore unevaluable. The
M5 plan does not contain an independently proven Step 3 edge that can be
implemented from this evidence.

Disposition: no code or runtime behavior change; do not repeat the parked
qualification and do not infer a writer, ordering edge, or audio cause from
the pre-title nulls. The next unit moves to a fresh systematic M3 idiom-class
census because the known M5 behavior-change gate is not satisfied.
