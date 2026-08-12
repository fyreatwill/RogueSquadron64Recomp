# NEXT work unit (static L_1268 continuation overlays 0x14 / 0x24)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s741 refuted H-ovl12-dma-wrap-stomp. Do not rebuild, resplice, or add
DMEM wrap. Classify the post-ovl12 `L_1268` exits against the ROM images
and the skipped IMEM DMA, using ROM / F5-UCODE-REFERENCE / the generated
dispatcher, not a new runtime counter.

## Competing hypotheses

- **H-ovl24-skipped-imem:** dominant `L_1F64` → `L_1268(r5=0x24)` DMA dest
  `0x12A0` is skipped (`dmem_addr & 0x1000`). `jr 0x12A0` runs main
  `L_12A0` (DL push) instead of overlay-24 (ROM `0x27260`, 0xE3 B, 215/227
  bytes differ from main). Fetch desyncs; table-`jr` UJs follow.
- **H-ovl14-window-collision:** rare DMA-path exit `L_1268(r5=0x14)` `jr`s
  `0x1DB0` into the spliced ovl12 image instead of ovl14 (ROM `0x26AB8`,
  0x21F B, 509/543 bytes differ from the window). Cannot explain ~31k
  `L_1F64` exits by itself.
- **H-r17-not-advanced:** overlay-12 never adds the GLideN64 `PC += 32`.
  Even a correct continuation overlay would then consume inline words as
  opcodes. Discriminate by whether ovl24's first instructions advance
  `r17` / consume `0x18..0x1E` vs treating `r20` as a DL pointer.

## Discriminating measurement

Static only, same iteration, no game run:

1. Disassemble ROM `0x27260..0x27343` (ovl24) vs main IMEM `0x12A0`
   (ROM `0x257D0`). Name ovl24's first `jr`/`j` and whether it is `L_12A0`
   semantics.
2. Disassemble ROM `0x26AB8..0x26CD7` (ovl14) vs spliced ovl12 at
   `0x1DB0`. Confirm it is not clip (ovl4) and not TriGen (ovl12).
3. `L_122C` dest for each `L_1268` path = delay-slot `lhu 0x76($3)`
   (already 0x1DB0 / 0x12A0). Confirm both skip in `dma_rdram_to_dmem`.
4. GLideN64 TriGen `PC += 32` vs ovl24's actual `r17` / PC effect.

Outcomes:

- ovl24 ≠ main `L_12A0` and ovl24 is the PC-advance / emit step →
  H-ovl24-skipped-imem SELECTED. Name that skipped IMEM writer before
  any new splice (fixup 6c candidate, not this iteration).
- ovl24 *is* a DL-push / `L_12A0` variant and ovl14 is the real
  continuation → H-ovl14-window-collision rises; still needs a reason
  the dominant path UJs.
- ovl24 clearly does `r17 += 32` (or equivalent) → H-r17-not-advanced
  becomes the skip consequence, not a third writer.

## Commands

    python3 - <<'PY'
    # dump first 16 words of ROM 0x27260 and 0x257D0; 0x26AB8 vs 0x26670
    PY
    # rabbitizer or existing scratch disasm helper if present
    # do not run the game
