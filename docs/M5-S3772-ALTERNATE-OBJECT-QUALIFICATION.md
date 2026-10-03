# M5 s3772 — alternate-object join qualification

The existing s3771 clear/object join was run twice with the retail oracle and
silent/image port arms. The first capture launched both port arms together;
the repaired capture staggered launch by two seconds.

In both captures the retail whole-RDRAM positive control fired and the oracle
reached title and hangar target VIs. The silent port arm passed all six
family-store controls, reached title `0x00790400` and hangar `0x006AB400`, and
emitted family-store rows. The image arm emitted controls but crashed before
target at `spTaskSchedulerThread+9556` (`last-guest-pc=0x8000834c`). It
therefore emitted no target-phase clear/object join rows.

The discriminator is unevaluable: `clear_span`/`clear_obj` and the I hangar
edge cannot be compared across qualified arms. The result does not select
alternate-object legitimacy, route/object mismatch, or the I hangar-edge
hypothesis. The launcher was repaired only to stagger arm startup; no game
value, clear, allocation, or audio gate changed.

Evidence: `scratch/agent/s3770_m5_family_store/` and the s3772 ledger entry.
