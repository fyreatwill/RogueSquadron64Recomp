# NEXT work unit — capture a new selector-producer context boundary

HYPOTHESIS-ID: m5-selector-producer-context

Session 3515 requalified retail `musyxMixActiveVoices` at `0x80090E04` in the
hangar with a whole-RDRAM positive control. Do not repeat the unchanged port
audio arms or unchanged retail capture.

Before building, identify one concrete new producer/context witness immediately
before selector stores at `0x8008F228`/`0x8008F264`; ask the retail oracle first
with whole-RDRAM and existing selector-store controls. Then add one
regeneration-safe port witness, build once, and run the validated
real-image/LLE/spin-yield/autopilot route with title and hangar buckets.

Competing hypotheses:

- `H-ContextProducerParity`: predecessor context matches retail; an earlier
  initializer or later mutation remains.
- `H-ContextProducerDivergence`: predecessor supplies different `s1` or related
  context; that producer edge is selected.
- `H-LaterContextMutation`: predecessor matches, but an intervening guest
  instruction mutates context before the writer.
- `H-CaptureInvalid`: whole-RDRAM, selector-store, or phase controls fail.

Discriminating measurement: matching predecessor fields with a later writer
difference selects mutation; the first differing predecessor field selects its
producer; failed controls select capture invalidity. Exact first command:
`tools/oracle/build/rs64_oracle ... --watch-write 0x0:0x800000
--watch-write <new-boundary> --watch-write 0x1149758:0x1149760 --vi-trace`.
Then run the one-build port capture with `ROGUESQ_LOG_M5_MIX_ENTRY=1` and the
new witness. Use SIGKILL, a non-dot final capture path, and run from `build/`.
