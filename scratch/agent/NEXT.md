# NEXT work unit (s2491) — preserve descriptor probe guest-pointer ABI

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Change the existing diagnostic callback boundary so
`rs64_m5_descriptor_yield` receives the guest task pointer with the runtime's
sign-extended `gpr` ABI instead of `uint32_t`; keep the generated call's
`U32(ctx->r4)` unchanged only if the callback re-sign-extends it before any
`MEM_W`/`TO_PTR` expression. Retain the comparison rows, raw-byte table, and
scheduler-id positive control. Do not change task dispatch, audio behavior, or
any guard.

Before building, verify the callback declaration and callsite types, then run
one Debug build and one qualified hangar capture with the oracle whole-RDRAM
positive control first. Use `ROGUESQ_LOG_AUDIO_RETURN=1`,
`ROGUESQ_LOG_M5_DESCRIPTOR=1`, `PROBE_PHASE_WIDTH=512`,
`PROBE_PHASE_TIMEOUT=300`, and the boot-relative eleven-Start schedule:
`6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start
46:start 51:start 56:start`. Do not use `PROBE_KEYS_FROM_PHASE=1`.

## Competing hypotheses and discriminator

- H-pointer-sign-extension-fixed: all three reads agree after preserving the
  `gpr` representation.
- H-pointer-ABI-not-causal: `MEM_W`/`TO_PTR` still disagree with explicit
  aligned bytes after the boundary fix.

The discriminator is the same-run equality table in the 512 /
`0x6AB400` phase, with descriptor and scheduler controls firing. Equality of
`MEM_W`, explicit reads, and `TO_PTR` selects the ABI explanation; continued
disagreement refutes it and reopens macro/layout handling. The oracle remains
a phase-independent positive control, not descriptor evidence.
