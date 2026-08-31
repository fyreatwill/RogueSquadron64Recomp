# NEXT work unit — qualify initN64RspMixer's caller chain

HYPOTHESIS-ID: m5-port-setup-state-producer

Session 3426 selected `H-CallerPassesPortCount`: retail supplies
`a1=0x561F` at `0x80091934`, while both port arms supply `a1=0x5622` at the
same init-to-allocate edge. The port init entry itself has `a1=0x0F`; the
earlier producer of the eventual `0x5622` remains open.

Competing hypotheses and the single discriminating measurement:

- `H-InitCallerParity`: retail and port enter `initN64RspMixer` from the same
  caller with matching `a0..a3`; the mismatch is in a later setup edge.
- `H-InitCallerContractGap`: retail and port have different init callers or
  entry arguments, locating the divergence before `initN64RspMixer`.
- `H-InitCallerUnevaluable`: the caller watch or phase controls disappear, so
  no init-caller conclusion is allowed.

Exact work: enumerate generated JALs to `0x80091898`; run the retail oracle
with `--watch-write 0x0:0x800000 --watch-pc 0x80091898
--pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512`
and the validated Start schedule; then use the already-built Debug target
with `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1` and the existing silent/image pair.
Keep title 1024, hangar 512, audio ABI/DMA, image-stage, and PCM controls.
Matching caller/argument tuples select parity; a retail/port mismatch selects
the contract gap; absent controls select unevaluable. Do not change waits,
slots, dispatch, clear behavior, or PCM writeback.
