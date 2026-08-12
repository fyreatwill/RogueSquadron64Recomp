# NEXT work unit (static DMEM-map / L_122C wrap audit)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s740 selected H-splice-correct. Do not rebuild or resplice. Classify the
new command-table UJ storm against overlay-12's two `L_122C` payload DMAs
using ROM / GLideN64 / F5-UCODE-REFERENCE ground truth, not a new runtime
counter.

## Competing hypotheses

- **H-ovl12-dma-wrap-stomp:** overlay-12 `L_122C` dests `r3=0x4E0` then
  `r3=0x380` with `r4` near `0xFF0` wrap 4 KB DMEM and overwrite command
  tables at `0x64` / `0xD6`. Later `L_1090`/`L_10C8` `jr` to OOB targets
  (`0xFA92`, `0x0000`, `0x4F42`).
- **H-ovl12-dma-legit-payload:** dests `0x380`/`0x4E0` are documented
  vertex/triangle scratch; legal sizes cannot cover `0x64`/`0xD6`. UJs
  then come from return-state / `L_1268` resident switch, not DMA wrap.
- **H-ovl12-imem-gap:** UJs are missing overlay-12 IMEM handlers. Already
  weak: s740 had **0** UJs in the `0x1DB0..0x1FE0` window.

## Discriminating measurement

Static only, same iteration, no game run:

1. `docs/F5-UCODE-REFERENCE.md` plus GLideN64 Factor 5 HLE: what lives at
   DMEM `0x64`, `0xD6`, `0x380`, `0x4E0`.
2. Overlay-12 translation (`factor5_ucode_ovl12_recompiled.c` `L_1DB0` body):
   the `r4` size formula at both `jal 0x122C` sites; max `dest+len` vs
   0x1000 wrap onto `0x64`/`0xD6`.
3. `L_122C` / `DO_DMA_READ` wrap semantics in our RSP.
4. Top s740 UJ targets vs those tables (file:
   `scratch/agent/soak_results/s739_ovl12_splice_20260812-152309/run.log`).

Outcomes:

- Wrap-capable size + dests cover the tables + OOB UJs match stomped
  halfwords → H-ovl12-dma-wrap-stomp. Then name the writer (command-stream
  length vs our DMA helper) before any change.
- Documented scratch + sizes cannot reach the tables → H-ovl12-dma-wrap
  REFUTED; next is `L_1268` resident-switch / `L_1FD4` delay-slot state.
- Dominant UJs land inside the overlay-12 window → reopen H-ovl12-imem-gap
  (s740 counts already contradict this).

## Commands

    python3 - <<'PY'
    # print both ovl12 jal 0x122C sites: r2/r3/r4 setup
    # classify dest+max_len wrap onto 0x64 and 0xD6
    PY
    grep -n '0x380\|0x4E0\|0x64\|0xD6' docs/F5-UCODE-REFERENCE.md docs/F5-UCODE-REFERENCE.md
    # GLideN64: search Factor5/F5 DMEM map for those addresses
    # DO_DMA_READ wrap: grep in lib/N64ModernRuntime or RSP recomp runtime
