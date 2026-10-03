# Next work unit: requalify the alternate-object join with image first

HYPOTHESIS-ID: m5-retail-writer-port-edge

The s3772 capture remained unevaluable twice: silent reached both target VIs,
but image crashed pre-target at `spTaskSchedulerThread+9556`, including after
a two-second stagger. Run one fresh concurrent retail-oracle/image/silent
capture with image launched first, retaining the existing family-store and
writer-setup logs. Do not add another field, change the clear, inject a
payload, or change an audio gate.

Competing hypotheses and the discriminating measurement:

- H1: S/L alternate stores belong to the legitimate clear-associated asset
  object; predicted `clear_span=1` with a stable `clear_obj`.
- H2: S/L stores belong to a distinct object/route and the route handoff is
  mismatched; predicted `clear_span=0` with stable clear and route identities.
- H3: I's missing hangar stores are an absent hangar edge rather than object
  mismatch; predicted I hangar rows or a positive retail/port I call edge with
  no generated store.

The discriminating measurement is one same-build capture that has the retail
whole-RDRAM positive control, both port target phases in both arms, and the
family-store controls. Compare `clear_span`, `clear_obj`, route ordinal, and
I hangar/call-edge rows in that one capture; any missing control makes the
result unevaluable.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3770_m5_family_store.sh

Before interpreting rows, require the oracle whole-RDRAM positive control and
both port arms' `origin=0x00790400` and `origin=0x006AB400` phase rows. The
family-store controls must fire in the same run. The new clear-join control is
the presence of `clear_obj=0x...` on family rows.

Discriminator:

- `clear_span=1` for alternate S/L rows, with a stable distinct clear object,
  supports a legitimate alternate asset object.
- `clear_span=0` with a stable clear object and matching route ordinals keeps
  route/object identity mismatch live.
- I rows in hangar, or a positive retail/port I call edge with no generated
  store, selects the I hangar-edge hypothesis.
- Missing either target phase or any positive control is an unevaluable
  qualification failure; repair/requalify rather than update the hypothesis
  table.
