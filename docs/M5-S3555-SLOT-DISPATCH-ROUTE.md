# M5 s3555 — slot-dispatch boundary was not reached

The existing regeneration-safe `ROGUESQ_LOG_SLOT_DISPATCH` table ran on the
canonical real-audio/LLE-solo/spin-yield/autopilot route with the slot-SP
guard enabled. Autopilot fired, VI widths reached 640 and 1024, and the
dispatcher emitted 2,048 entry, 2,048 pre-call, and 2,048 post-call rows in
phase 3. Every pre-call row had a valid KSEG0 slot pointer; no slot-SP guard
fired.

The run was route-invalid for the selected boundary. It exited at 41.9
seconds / 67 frames after a native crash in `musyxSynthFrame+3828`, with last
guest PC `0x80001B08`, rather than at the target dispatcher failure
(`0x80007904`). The dispatcher table therefore does not distinguish invalid
input, lifecycle route, or overlay dispatch for the s3554 failure.

This is single-source port evidence. It rules out only a missing instrument or
missing positive control in this capture. It does not establish dispatcher
input legitimacy or identify the writer of the separate MusyX crash input.

ORIGIN: no mitigation or value rewrite was added. The sampled slot pointers
are guest-owned diagnostic state; legitimacy at the s3554 failure remains
unresolved.
