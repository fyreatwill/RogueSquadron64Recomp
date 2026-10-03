# M5 s3771 — alternate-object join instrumentation

The work unit was to join the s3770 family-store destinations to the object
allocated and cleared at `0x8008F2CC`, with the active route ordinal/row, in a
same-build retail-oracle/image/silent capture.

The host witness records `clear_obj`, exact-object membership, and membership
within the `0x298`-byte allocation span on each existing S/L/I family-store
row. The clear snapshot is process-wide because the clear and family writers
may execute on different runtime threads. The generated call is now
regeneration-safe in `fixup_game_funcs.py` and passes the generated host
`rdram` argument; the first attempt exposed the missing argument through a
crash inside the witness and was corrected before the final build.

The Debug build passed. The final paired capture did not qualify: both port
arms stopped before title at the known `spTaskSchedulerThread+9556` crash
boundary, so no target family rows or clear join rows were available. The
retail oracle fired its whole-RDRAM positive-control threshold but did not
reach a target phase in this capture. Earlier s3770 family controls therefore
cannot be reused as a positive control for this new clear-join field.

Conclusion: no alternate-object or route-identity hypothesis is selected or
refuted. This is a qualification failure, not evidence that the join is
absent. No game value, clear, allocation, or audio gate was changed.

ORIGIN: the family stores and clear allocation are legitimate existing game
operations; the added fields are diagnostic-only.
