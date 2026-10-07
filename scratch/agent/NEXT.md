# Next work unit: qualify the first body loads at 0x8008F900

HYPOTHESIS-ID: m5-step4-object-entry-body

Session 4181 repaired the predecessor witness's raw-address semantics and
qualified parity at the shared hangar phase. The next boundary is inside
`0x8008F900`; use one batched, regeneration-safe witness for its first body
loads and compare the values against an independent oracle watch.

Competing hypotheses:

- H-body-input-mismatch: a first body load/input differs between retail and
  port after the matched predecessor context.
- H-body-input-parity: body inputs match, moving the boundary to the next
  instruction or consumer.
- H-route-invalid: the independent body watch or phase joins do not qualify;
  no conclusion is allowed.

Discriminator: one build/run with the whole-RDRAM positive control, both retail
target phases (`0x00790400`/`0x006AB800`), both port target phases, and joined
`0x8008F8FC`/`0x8008F900` body rows. A comparable body-input mismatch selects
the first divergent load; parity moves the boundary inward; missing controls
or joins is unevaluable. Do not change audio, gate, writer, payload, or
mitigation logic.

Exact work:

1. Add one witness at the first body loads after `0x8008F900`, recording the
   raw register/address/value tuple with a phase-scoped budget; do not alter
   guest behavior.
2. Add the matching oracle watch/field dump to the paired recipe, using retail
   hangar origin `0x006AB800` and port hangar origin `0x006AB400`.
3. Build once, run both arms concurrently, and require the positive-control
   line, retail title/hangar, port title/hangar, 71 retail predecessor hits,
   and two port joins before judging any null or mismatch.

Use [F5-UCODE-REFERENCE.md](../../docs/F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. MusyX/MORT audio remains partially stubbed; do not send
MusyX data to stock `aspMain`.
