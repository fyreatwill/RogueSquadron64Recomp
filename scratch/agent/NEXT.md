# NEXT work unit — witness both initN64RspMixer callsites

HYPOTHESIS-ID: m5-port-setup-state-producer

Session 3427 selected a retail/port caller-site asymmetry: retail executes
`0x80091D14`, while the current port entry witness cannot recover a caller
because `ctx->r31` is zero. Session 3426 established that retail supplies
`a1=0x561F` at `0x80091934`, while both port arms supply `a1=0x5622` at the
same init-to-allocate edge. The port init entry itself has `a1=0x0F`; the
earlier producer of the eventual `0x5622` remains open.

Competing hypotheses and the single discriminating measurement:

- `H-PortCallerD1D14`: a direct port callsite witness identifies
  `0x80091D14`, matching retail's independent `prev_pc`.
- `H-PortCallerD1C58`: the port reaches init through the other generated
  callsite `0x80091C58`.
- `H-PortCallerUnresolved`: neither callsite witness fires despite live phase,
  init, and audio controls, so the direct-call mapping needs a different edge.

Exact work: add one regeneration-safe, phase-gated host witness at each of the
two generated callsites (`0x80091C58` and `0x80091D14`) recording the callsite
and `a0..a3`; build once; run the existing silent/image pair concurrently
with `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1`. Keep title 1024, hangar 512, audio
ABI/DMA, image-stage, and PCM controls. Matching `0x80091D14` selects
`H-PortCallerD1D14`; `0x80091C58` selects `H-PortCallerD1C58`; no callsite
rows with live controls selects `H-PortCallerUnresolved`. Do not change
waits, slots, dispatch, clear behavior, or PCM writeback.
