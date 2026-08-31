# M5 Session 3480 — late-store boundary

The independent retail preflight used the Rice route, a whole-RDRAM write
control, and execution watches at `0x80033410` plus the six selected late
`rs_free` PCs. It ran 35 seconds, reached title origin `0x00790400` at width
1024, and recorded 10,000 whole-RDRAM control hits. `0x80033410` was active;
the six late PCs each recorded zero executions.

The rebuilt port used the validated LLE/spin-yield image route with
`ROGUESQ_M5_DOWNSTREAM_LATE_ONLY=1`. It reached title origin
`0x00790400`, fired the host-boundary positive control once, emitted 483
host-task rows and 512 `osSendMesg` return rows, and emitted zero late-store
positive-control or late-store rows. The generated source contains the
regeneration-safe helper at all six selected PCs, so this null is qualified
as an unexecuted guest-store path, not a missing hook.

Together these two lines rule out the selected six late guest PCs as the
first mutation at the observed title boundary. They do not by themselves
prove which host contract differs. The next discriminator is a phase/ordinal
join of the port host-task fields against an independent retail task dump,
with the existing whole-RDRAM and host controls retained.
