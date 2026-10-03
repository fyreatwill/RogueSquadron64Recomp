# M5 s3773 — image-first alternate-object qualification

The rebuilt Debug binary ran `scratch/agent/run_s3770_m5_family_store.sh`,
launching the image arm first, then the silent arm, beside the retail oracle.
The oracle whole-RDRAM positive control fired. Image passed the family-store
controls and reached title `1024 @ 0x00790400` at 13.5s and hangar
`512 @ 0x006AB400` at 33.7s. Silent passed the same controls but crashed
before either target VI at `spTaskSchedulerThread+9556`, with
`last-guest-pc=0x8000834c`.

This is a qualification failure, not a null result for the clear/object join:
the required paired silent target phase is absent. Image-first ordering did
not remove the silent pre-target instability in this capture. The image arm's
target rows cannot select legitimate alternate-object provenance versus
route/object mismatch without the planned paired control; the I hangar edge is
likewise unevaluable. This is single-capture evidence. Logs are in
`scratch/agent/s3770_m5_family_store/`.

The repeated paired qualification is parked after s3771–s3773. The next
probe is image-only plus retail oracle, using the existing phase-gated
clear/object and family-edge fields; it must not be treated as a substitute
for the silent control when interpreting arm differences.
