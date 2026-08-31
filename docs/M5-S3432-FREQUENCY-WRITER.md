# M5 Session 3432 — frequency-result writer qualification

The prescribed retail oracle run passed its same-run whole-RDRAM positive control
(10,041 callbacks) and reached 7,195 VI. The exact phase buckets did not arm,
so the oracle could not provide title/hangar attribution. A lower-noise retry
still passed the control and observed 41 writes to physical `0x165ED0`; its
lifetime writer histogram included `0x800331E0` (2), `0x80007670` (4),
`0x80023D7C` (14), and setup/initialization PCs. This is not an exact
frequency-return attribution.

The fixed sequential port pair passed title 1024 and hangar 512 in both silent
and image arms, with no crash or abort markers. Both arms reported the same
phase-qualified chain: `osAiSetFrequency` returned `0x5622` in title and
hangar; the subsequent mixer/allocate path used `a1=0x0F` in title and
`a1=0x12` in hangar, with the `0x8009192C` reload supplying `0x5622` to the
allocate call. The concurrent version was not used because both arms hit the
known pre-phase scheduler crash before any control row.

This gives two independent lines for the port result and refutes a silent/image
arm difference at the observed boundary. It does not select between the retail
writer hypotheses: the oracle phase signal failed to arm, and its lifetime
histogram contains multiple legitimate writers. No runtime behavior changed.

Evidence: `scratch/agent/s3432_m5_frequency_writer/`.
