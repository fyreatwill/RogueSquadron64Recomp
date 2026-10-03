# Next work unit: qualify the repaired alternate-object join

HYPOTHESIS-ID: m5-retail-writer-port-edge

The s3771 join is ABI-correct and built, but the paired capture was
unevaluable because both port arms stopped before target. Run one fresh
concurrent retail-oracle/image/silent capture with the existing family-store
and writer-setup logs. Do not add another field, change the clear, inject a
payload, or change an audio gate.

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
