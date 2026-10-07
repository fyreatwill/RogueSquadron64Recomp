# Next work unit: repair the port predecessor field witness

HYPOTHESIS-ID: m5-step4-object-field-producer

The s4180 paired run qualified the route and matched predecessor registers
(`s0=0x48`, `s1=0x1B000`) but exposed a witness alias: the port helper's
KSEG-only guards turn the low raw predecessor fields into `0xFFFFFFFF`, while
the independent oracle reads the corresponding raw RDRAM fields. Make the
diagnostic witness use the same raw-address semantics for this predecessor,
without changing guest behavior, then rerun the paired oracle/port route.

Competing hypotheses:

- H-earlier-producer-mismatch: comparable source/branch fields still diverge
  after the witness semantics are repaired.
- H-entry-body-mismatch: predecessor fields match, so divergence begins in the
  `0x8008F900` body or its immediate loads.
- H-measurement-alias: the repaired raw-address witness reconciles the apparent
  divergence, leaving the current boundary unevaluable or moving it inward.

Discriminator: one build/run with the whole-RDRAM positive control, both retail
target phases (`0x00790400`/`0x006AB400`), both port target phases, and joined
predecessor rows. A comparable nonzero field mismatch selects the earlier
producer; parity selects the entry body; missing controls or joins is
unevaluable. Do not change audio, gate, writer, payload, or mitigation logic.

Exact work:

1. In `rs64_m5_object_entry_witness`, preserve the register snapshot but read
   the low raw addresses with the same physical/RDRAM semantics as the oracle;
   keep the existing KSEG behavior for ordinary object pointers if needed and
   label the raw-address branch explicitly.
2. Build the normal target from `build/` and run
   `zsh scratch/agent/run_s4180_m5_predecessor_context.sh`, using a fresh OUT
   directory or verified child cleanup. Keep `ROGUESQ_LOG_M5_OBJECT_ENTRY=1`,
   `ROGUESQ_LOG_M5_OBJECT_FIELD=1`, and all route flags already in the recipe.
3. Require the positive-control line, retail title/hangar, port title/hangar,
   71 retail predecessor hits, and two port predecessor joins before judging
   any null or mismatch.

Use [F5-UCODE-REFERENCE.md](../../docs/F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. MusyX/MORT audio remains partially stubbed; do not send
MusyX data to stock `aspMain`.
