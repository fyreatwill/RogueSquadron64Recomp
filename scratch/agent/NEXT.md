# NEXT work unit (s2473) — locate the runtime entry that constructs mainGameLoop context

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Audit the host/runtime and overlay registration path that invokes the
generated `mainGameLoop` entry at `0x8003DFA0`. Start with the function-map
registration and the entrypoint/thread startup callsites; identify every path
that can call `mainGameLoop`, and capture the context initialization immediately
before the live entry. Do not add a guard, stub, dispatch, audio, output, or
task-data change.

## Competing hypotheses and discriminator

- H-RuntimeZero: runtime entry construction initializes or preserves `r31=0`.
- H-OverlayWrapper: an overlay wrapper or trampoline supplies the zero before
  entering `mainGameLoop`.
- H-ContextClobber: the context is nonzero at construction but is cleared by
  an intervening host/generated boundary.

The complete static caller/registration table plus one same-run entry-side
capture of the constructed context discriminates these: a zero in the runtime
construction selects H-RuntimeZero; a wrapper/trampoline row with zero selects
H-OverlayWrapper; nonzero construction followed by entry zero selects
H-ContextClobber. Retain the `0x8009123C` resolver positive control and the
retail whole-RDRAM/exact-range controls before trusting a null.

## Commands

1. Grep the host runtime, overlay registration, and generated lookup tables for
   `mainGameLoop`, `0x8003DFA0`, and the entrypoint symbol; record all candidate
   callsites before instrumentation.
2. Ask the retail oracle first with Rice, whole-RDRAM positive control, exact
   range watches, VI trace, and the established Start schedule.
3. Add one batched construction/entry capture in the durable fixup or host
   source, rebuild once, and run from `build/` with
   `ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1
   ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_PRETARGET=1`.
   Kill with SIGKILL and write
   `scratch/agent/s2473_m5_runtime_entry_boundary/audit.md`.
