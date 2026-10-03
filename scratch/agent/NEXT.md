# Next work unit: compare qualified retail and port route state

HYPOTHESIS-ID: m5-route-state-parity

s3788 qualified the Start+Z recipe with Rice: whole-RDRAM fired 10,018 times,
target VIs appeared, and all three family PCs executed. Use the existing paired
route-state capture to compare retail's independently watched route bytes with
the port's phase-gated family-entry rows.

Competing hypotheses and discriminator:

- H1: retail route bytes and port family-entry bytes show the same route state,
  supporting route parity and moving the boundary downstream.
- H2: retail family PCs execute but route bytes differ from the port's zero
  rows, proving a route-state mismatch rather than a source-payload absence.
- H3: the paired capture lacks a positive control, target phase, or port family
  rows, so the comparison is unevaluable and the capture recipe is at fault.

The discriminating measurement is one paired capture with a whole-RDRAM oracle
control, retail route-byte watches, and port family-entry route rows in the
same target VI phases. H1/H2 are decided only after both arms have positive
controls and target-family rows; a missing control invalidates that arm.

Exact command:

    zsh scratch/agent/run_s3769_m5_family_entry.sh
    grep -a -E 'positive-control|watch write|watch pc|origin=0x00790400|origin=0x006ab400|m5-family-guest-route' \
      scratch/agent/s3769_m5_family_entry/oracle.log \
      scratch/agent/s3769_m5_family_entry/image.log

Require the oracle positive control, title/hangar VIs, and all three port
family-entry controls before comparing values. Do not infer route identity from
route-byte writes alone.
