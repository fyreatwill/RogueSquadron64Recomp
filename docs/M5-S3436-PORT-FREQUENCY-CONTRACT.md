# M5 Session 3436 — port frequency-contract witness boundary

The required retail ground-truth attempt passed the whole-RDRAM control and
armed both title origins, but watched-PC output flooded the capture and the
process was SIGKILLed before final summaries. The prior Session 3435 retail
field-family census remains the qualified ground truth.

The port was rebuilt once and run on the qualified Factor 5 image route. The
phase/title and hangar controls fired, the image-stage control produced 4,789
rows, and there were no crash or abort markers. The new witness produced 256
bounded rows, all in title origin `0x00790400`; no `0x00790800` row occurred.

The raw tuple set had 107 distinct rows. It had no exact intersection with the
6,825 distinct retail `pc-field-dump` rows retained from the ground-truth
attempt. This result is not a valid selection of `H-PortTupleFamilyMissing`:
retail PC `0x800331E0` is inside `osRecvMesg`, whereas the port witness is at
the host `osRecvMesg_recomp` entry. The port `$s0/$s1` and pointed-field values
are consequently sampled at different execution boundaries. The result
selects `H-PhaseJoinMissing` for this instrument and leaves the port tuple
family unevaluable. No audio behavior or dispatch path changed.

The witness remains useful only after moving the retail control to the
`osRecvMesg` entry at `0x800331D0`, which is the next boundary that can be
joined to the port wrapper entry.
