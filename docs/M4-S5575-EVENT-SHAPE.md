# M4 Session 5575 — event-shape boundary

## Work unit

Compare the qualified retail capture and the s5568b port capture with a new
boundary key, `(VI phase, ucode image, mapped IMEM PC, task-total bucket)`.
This is not the prior exact progress join or the prior ordered rank-bin join.
The analyzer is `tools/analyze_m4_event_shape.py`.

## Controls and result

Both arms passed whole-RDRAM, VI, mapped-PC, and image controls. Retail
contributed 2,573,768 hangar rows; port contributed 1,220,601. The lane field
was active in both arms (retail 57,627 rows; port 47,657 rows), so the positive
control is not a counter-only branch witness.

The proposed key formed zero shared classes: retail had 656 classes (328 per
mapped PC), while port had six (three per mapped PC). H3 is selected: the
task-total bucket is not portable, despite active lane data and passing
controls. No writer, legitimacy, or mitigation conclusion follows. This rules
out only this key as a usable cross-arm boundary.
