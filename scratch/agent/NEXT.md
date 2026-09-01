# NEXT work unit — identify internal AI-frequency return semantics

HYPOTHESIS-ID: m5-selector-ai-return-semantics

Session 3533 qualified the split independently: retail entered `0x80029D20`
with `a0=0x5622` and had `v0=0x561F` at `0x80091CC4`; the port setup return
row had `v0=0x5622`. The new host return probe had a startup control but no
target-phase row and is not evidence.

Next unit: use static source/ABI evidence or one genuinely new paired boundary
to identify why `0x80029D20` returns `0x561F` on retail but the port host
implementation returns its input `0x5622`. Do not change audio/selector/task/
output state.

Competing hypotheses and discriminator:

- `H-InternalReturnSemantics`: retail's internal function contract differs
  from the port host implementation; static semantics or a new boundary
  should explain the mapped return.
- `H-LaterStoreABI`: the internal return matches but the port's setup/store
  context changes it later.
- `H-CaptureInvalid`: a required positive control or target execution witness
  is absent; no semantic conclusion is allowed.

Required discriminator: source-level contract or paired observation that
either explains the `0x561F` return from `0x5622`, or proves the value changes
after `0x80029D20` and before `0x80091CC4`.
